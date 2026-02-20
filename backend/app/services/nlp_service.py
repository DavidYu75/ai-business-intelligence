"""
NLP service for natural language to SQL conversion using Claude API.

Provides schema-aware prompting and SQL validation.
"""

import json
import re
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings


class NLPService:
    """Service for converting natural language queries to SQL using Claude."""

    # Maximum rows to hint in prompt to avoid huge queries
    MAX_RESULT_ROWS = 1000

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.model = settings.CLAUDE_MODEL
        self.api_url = "https://api.anthropic.com/v1/messages"

    def _build_schema_context(self, schema: Dict[str, Any]) -> str:
        """
        Build a concise schema description for the Claude prompt.

        Args:
            schema: Database schema dict from DatabaseAdapter.get_schema()

        Returns:
            Formatted schema string
        """
        lines = ["DATABASE SCHEMA:"]

        tables = schema.get("tables", {})
        for table_name, table_info in tables.items():
            columns = table_info.get("columns", [])
            row_count = table_info.get("row_count")

            col_defs = []
            for col in columns:
                col_str = f"  - {col['name']} ({col['type']}"
                if not col.get("nullable", True):
                    col_str += ", NOT NULL"
                col_str += ")"
                col_defs.append(col_str)

            pks = table_info.get("primary_keys", [])
            pk_str = f"  Primary Key: {', '.join(pks)}" if pks else ""

            row_str = f"  (~{row_count} rows)" if row_count is not None else ""

            lines.append(f"\nTable: {table_name}{row_str}")
            if pk_str:
                lines.append(pk_str)
            lines.extend(col_defs)

        return "\n".join(lines)

    def _build_prompt(
        self,
        query: str,
        schema: Dict[str, Any],
    ) -> str:
        """
        Build the system prompt for Claude.

        Args:
            query: Natural language query from user
            schema: Database schema

        Returns:
            System prompt string
        """
        schema_context = self._build_schema_context(schema)

        return f"""You are a SQL expert that converts natural language questions into PostgreSQL queries.

{schema_context}

RULES:
1. Generate ONLY a valid PostgreSQL SELECT query. Never generate INSERT, UPDATE, DELETE, DROP, or any data-modifying statements.
2. Use only tables and columns that exist in the schema above.
3. Always use double quotes around identifiers that might be reserved words or mixed case.
4. Add LIMIT {self.MAX_RESULT_ROWS} to prevent overly large result sets, unless the user explicitly asks for all results.
5. For aggregation queries, include meaningful column aliases using AS.
6. Use appropriate JOINs when the query spans multiple tables.
7. If the query is ambiguous, make reasonable assumptions and proceed.
8. Return ONLY the SQL query, no explanations, no markdown formatting, no code blocks.

EXAMPLES:
- "show me total sales by month" → SELECT DATE_TRUNC('month', created_at) AS month, SUM(amount) AS total_sales FROM orders GROUP BY month ORDER BY month LIMIT {self.MAX_RESULT_ROWS}
- "how many users signed up last week" → SELECT COUNT(*) AS user_count FROM users WHERE created_at >= NOW() - INTERVAL '7 days'
- "top 10 products by revenue" → SELECT product_name, SUM(price * quantity) AS revenue FROM order_items JOIN products ON order_items.product_id = products.id GROUP BY product_name ORDER BY revenue DESC LIMIT 10"""

    def _validate_sql(self, sql: str) -> str:
        """
        Validate and sanitize generated SQL.

        Args:
            sql: Generated SQL string

        Returns:
            Cleaned SQL string

        Raises:
            ValueError: If SQL contains dangerous operations
        """
        # Clean up the SQL
        sql = sql.strip()

        # Remove markdown code blocks if present
        sql = re.sub(r"^```(?:sql)?\s*", "", sql)
        sql = re.sub(r"\s*```$", "", sql)
        sql = sql.strip()

        # Remove trailing semicolons
        sql = sql.rstrip(";").strip()

        # Validate it's a SELECT / WITH statement
        normalized = sql.upper().strip()
        if not normalized.startswith("SELECT") and not normalized.startswith("WITH"):
            raise ValueError(
                "Generated query is not a SELECT statement. "
                "Only read-only queries are supported."
            )

        # Block dangerous keywords
        dangerous = [
            "INSERT INTO",
            "UPDATE ",
            "DELETE FROM",
            "DROP ",
            "TRUNCATE ",
            "ALTER ",
            "CREATE ",
            "GRANT ",
            "REVOKE ",
            "EXEC ",
            "EXECUTE ",
        ]
        for keyword in dangerous:
            if keyword in normalized:
                raise ValueError(
                    f"Generated query contains forbidden operation: {keyword.strip()}"
                )

        return sql

    async def generate_sql(
        self,
        natural_language_query: str,
        schema: Dict[str, Any],
    ) -> str:
        """
        Convert a natural language query to SQL using Claude.

        Args:
            natural_language_query: User's question in plain English
            schema: Database schema dictionary

        Returns:
            Generated SQL query string

        Raises:
            ValueError: If SQL validation fails
            httpx.HTTPError: If Claude API call fails
        """
        system_prompt = self._build_prompt(natural_language_query, schema)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.api_url,
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": self.model,
                    "max_tokens": 1024,
                    "system": system_prompt,
                    "messages": [
                        {
                            "role": "user",
                            "content": natural_language_query,
                        }
                    ],
                },
            )

            if response.status_code != 200:
                error_detail = response.text
                raise ValueError(
                    f"Claude API error (status {response.status_code}): {error_detail}"
                )

            data = response.json()
            generated_sql = data["content"][0]["text"]

        # Validate the SQL
        validated_sql = self._validate_sql(generated_sql)

        return validated_sql
