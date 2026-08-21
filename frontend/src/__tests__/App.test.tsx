import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import App from "../App";

describe("App", () => {
  it("renders login page by default", () => {
    render(<App />);
    expect(screen.getByText(/AI Customer Operations/)).toBeDefined();
  });

  it("shows sign in form", () => {
    render(<App />);
    expect(screen.getByText("Sign In")).toBeDefined();
    expect(screen.getByLabelText("Email")).toBeDefined();
    expect(screen.getByLabelText("Password")).toBeDefined();
  });
});
