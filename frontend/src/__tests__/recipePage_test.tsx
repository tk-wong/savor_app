import React from "react";
import { render } from "@testing-library/react-native";
import RecipePageRoute from "../app/recipePage";

jest.mock("../screens/recipePage", () => ({
  __esModule: true,
  default: () => null,
}));

describe("Recipe page route", () => {
  it("renders recipe page route without crashing", () => {
    expect(() => render(<RecipePageRoute />)).not.toThrow();
  });
});
