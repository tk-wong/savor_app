import React from "react";
import { render } from "@testing-library/react-native";
import ChatPageRoute from "../app/(tabs)/chatPage";

jest.mock("../screens/chatPage", () => ({
  __esModule: true,
  default: () => null,
}));

describe("Chat page route", () => {
  it("renders chat page route without crashing", () => {
    expect(() => render(<ChatPageRoute />)).not.toThrow();
  });
});
