import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "./card";

describe("Card Components", () => {
  it("renders a basic card with content", () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Test Title</CardTitle>
          <CardDescription>Test Description</CardDescription>
        </CardHeader>
        <CardContent>
          <p>Main content</p>
        </CardContent>
        <CardFooter>
          <button>Action</button>
        </CardFooter>
      </Card>
    );

    expect(screen.getByText("Test Title")).toBeInTheDocument();
    expect(screen.getByText("Test Description")).toBeInTheDocument();
    expect(screen.getByText("Main content")).toBeInTheDocument();
    expect(screen.getByText("Action")).toBeInTheDocument();
  });

  it("applies data-slot attributes correctly", () => {
    const { container } = render(<Card />);
    expect(container.firstElementChild).toHaveAttribute("data-slot", "card");
  });

  it("applies custom className", () => {
    const { container } = render(<Card className="custom-card-class" />);
    expect(container.firstChild).toHaveClass("custom-card-class");
  });
});
