import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

// Simple test component for testing setup
const TestComponent = () => {
  return <div data-testid="test-component">Hello, Testing!</div>;
};

describe('Frontend Testing Setup', () => {
  test('renders test component', () => {
    render(<TestComponent />);
    const element = screen.getByTestId('test-component');
    expect(element).toBeInTheDocument();
    expect(element).toHaveTextContent('Hello, Testing!');
  });

  test('basic JavaScript functionality', () => {
    expect(2 + 2).toBe(4);
    expect('hello'.toUpperCase()).toBe('HELLO');
  });
});
