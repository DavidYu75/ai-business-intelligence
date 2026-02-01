import { render, screen } from '@testing-library/react'
import Home from '../index'

describe('Home Page', () => {
  it('renders the welcome message', () => {
    render(<Home />)
    
    expect(screen.getByText(/Real-Time Business Intelligence Platform/i)).toBeInTheDocument()
    expect(screen.getByText(/Welcome to the Real-Time BI Platform/i)).toBeInTheDocument()
  })

  it('renders the API documentation link', () => {
    render(<Home />)
    
    const apiLink = screen.getByRole('link', { name: /API Documentation/i })
    expect(apiLink).toBeInTheDocument()
    expect(apiLink).toHaveAttribute('href', 'http://localhost:8000/docs')
  })

  it('renders the development environment status', () => {
    render(<Home />)
    
    expect(screen.getByText(/Development environment is running/i)).toBeInTheDocument()
  })

  it('renders the backend health check link', () => {
    render(<Home />)
    
    const healthLink = screen.getByRole('link', { name: /Backend Health Check/i })
    expect(healthLink).toBeInTheDocument()
    expect(healthLink).toHaveAttribute('href', 'http://localhost:8000/health')
  })
})
