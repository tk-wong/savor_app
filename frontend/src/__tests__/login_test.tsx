// File: __tests__/index_test.tsx
import React from "react";
import { Alert } from "react-native";
import { fireEvent, render, screen, waitFor } from "@testing-library/react-native";
import LoginPage from "../app/loginPage";
import { login } from "../api";
import { router } from "expo-router";

jest.mock("../api", () => ({
  login: jest.fn(),
}));

jest.mock("expo-router", () => ({
  router: {
    push: jest.fn(),
    navigate: jest.fn(),
  },
  Stack: {
    Screen: () => null,
  },
}));

describe("Login screen", () => {
  const alertMock = jest.spyOn(Alert, "alert");
  const mockedLogin = login as jest.MockedFunction<typeof login>;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterAll(() => {
    alertMock.mockRestore();
  });

  it("renders login inputs and actions", () => {
    render(<LoginPage />);

    expect(screen.getByPlaceholderText("Enter your email")).toBeTruthy();
    expect(screen.getByPlaceholderText("Enter your password")).toBeTruthy();
    expect(screen.getByText("Submit")).toBeTruthy();
    expect(screen.getByText("Create account")).toBeTruthy();
    expect(screen.getByText("Reset")).toBeTruthy();
  });

  it("shows validation error and skips API call when required fields are missing", () => {
    render(<LoginPage />);

    fireEvent.press(screen.getByText("Submit"));

    expect(alertMock).toHaveBeenCalledWith("Error", "Please enter both email and password");
    expect(mockedLogin).not.toHaveBeenCalled();
  });

  it("logs in successfully and navigates to chat page", async () => {
    mockedLogin.mockResolvedValue({} as any);
    render(<LoginPage />);

    fireEvent.changeText(screen.getByPlaceholderText("Enter your email"), "user@example.com");
    fireEvent.changeText(screen.getByPlaceholderText("Enter your password"), "secret");
    fireEvent.press(screen.getByText("Submit"));

    await waitFor(() => {
      expect(mockedLogin).toHaveBeenCalledWith("user@example.com", "secret");
    });
    expect(alertMock).toHaveBeenCalledWith("Login successful");
    expect(router.push).toHaveBeenCalledWith("/chatPage");
  });

  it("shows an error alert when login fails", async () => {
    mockedLogin.mockRejectedValue("Bad credentials");
    render(<LoginPage />);

    fireEvent.changeText(screen.getByPlaceholderText("Enter your email"), "user@example.com");
    fireEvent.changeText(screen.getByPlaceholderText("Enter your password"), "wrong");
    fireEvent.press(screen.getByText("Submit"));

    await waitFor(() => {
      expect(alertMock).toHaveBeenCalledWith("Login failed", "Error: Bad credentials");
    });
    expect(router.push).not.toHaveBeenCalledWith("/chatPage");
  });

  it("clears both inputs when Reset is pressed", () => {
    render(<LoginPage />);

    const emailInput = screen.getByPlaceholderText("Enter your email");
    const passwordInput = screen.getByPlaceholderText("Enter your password");

    fireEvent.changeText(emailInput, "user@example.com");
    fireEvent.changeText(passwordInput, "secret");
    fireEvent.press(screen.getByText("Reset"));

    expect(emailInput.props.value).toBe("");
    expect(passwordInput.props.value).toBe("");
  });

  it("navigates to create user page", () => {
    render(<LoginPage />);

    fireEvent.press(screen.getByText("Create account"));

    expect(router.navigate).toHaveBeenCalledWith("/createUserPage");
  });
});
