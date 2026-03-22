import React from "react";
import { Alert, View, TextInput } from "react-native";
import { fireEvent, render, screen, waitFor } from "@testing-library/react-native";
import CreateUserPage from "../screens/createUserPage";
import { createUser } from "../api";
import { useRouter } from "expo-router";
import { isAxiosError } from "axios";

jest.mock("../api", () => ({
  createUser: jest.fn(),
}));

jest.mock("axios", () => ({
  isAxiosError: jest.fn(),
}));

jest.mock("expo-router", () => ({
  useRouter: jest.fn(),
  Stack: {
    Screen: () => null,
  },
}));

jest.mock("react-native-safe-area-context", () => {
  const { View } = require("react-native");
  return {
    SafeAreaView: ({ children }: { children: React.ReactNode }) => <View>{children}</View>,
    useSafeAreaInsets: jest.fn(() => ({ top: 0, right: 0, bottom: 0, left: 0 })),
  };
});

describe("CreateUserPage", () => {
  const mockedCreateUser = createUser as jest.MockedFunction<typeof createUser>;
  const mockedUseRouter = useRouter as jest.Mock;
  const mockedIsAxiosError = isAxiosError as unknown as jest.Mock;
  const alertMock = jest.spyOn(Alert, "alert");
  const navigateMock = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    mockedUseRouter.mockReturnValue({ navigate: navigateMock });
    mockedIsAxiosError.mockReturnValue(false);
  });

  afterAll(() => {
    alertMock.mockRestore();
  });

  it("shows validation alert when required fields are missing", async () => {
    render(<CreateUserPage />);

    fireEvent.press(screen.getByText("Submit"));

    expect(alertMock).toHaveBeenCalledWith("Error", "Please fill in all fields");
    expect(mockedCreateUser).not.toHaveBeenCalled();
  });

  it("creates user successfully and navigates to login page", async () => {
    mockedCreateUser.mockResolvedValue({} as any);

    render(<CreateUserPage />);

    const inputs = screen.UNSAFE_getAllByType(TextInput);
    fireEvent.changeText(inputs[0], "new_user");
    fireEvent.changeText(inputs[1], "new@example.com");
    fireEvent.changeText(inputs[2], "password123");
    fireEvent.press(screen.getByText("Submit"));

    await waitFor(() => {
      expect(mockedCreateUser).toHaveBeenCalledWith("new@example.com", "new_user", "password123");
    });
    expect(alertMock).toHaveBeenCalledWith("User created", "User created successfully! Please log in.");
    expect(navigateMock).toHaveBeenCalledWith("/loginPage");
  });

  it("shows conflict message when API returns 409 axios error", async () => {
    mockedCreateUser.mockRejectedValue({ status: 409, message: "Conflict" });
    mockedIsAxiosError.mockReturnValue(true);

    render(<CreateUserPage />);

    const inputs = screen.UNSAFE_getAllByType(TextInput);
    fireEvent.changeText(inputs[0], "existing_user");
    fireEvent.changeText(inputs[1], "existing@example.com");
    fireEvent.changeText(inputs[2], "password123");
    fireEvent.press(screen.getByText("Submit"));

    await waitFor(() => {
      expect(alertMock).toHaveBeenCalledWith(
        "Error",
        "User already exists. Please use a different email or username.",
      );
    });
  });

  it("shows invalid input message when API returns 400 axios error", async () => {
    mockedCreateUser.mockRejectedValue({ status: 400, message: "Bad input" });
    mockedIsAxiosError.mockReturnValue(true);

    render(<CreateUserPage />);

    const inputs = screen.UNSAFE_getAllByType(TextInput);
    fireEvent.changeText(inputs[0], "new_user");
    fireEvent.changeText(inputs[1], "new@example.com");
    fireEvent.changeText(inputs[2], "password123");
    fireEvent.press(screen.getByText("Submit"));

    await waitFor(() => {
      expect(alertMock).toHaveBeenCalledWith(
        "Error",
        "Invalid input. Please check your email, username, and password.",
      );
    });
  });

  it("shows generic axios failure message for non-400/non-409 status", async () => {
    mockedCreateUser.mockRejectedValue({ status: 500, message: "Server error" });
    mockedIsAxiosError.mockReturnValue(true);

    render(<CreateUserPage />);

    const inputs = screen.UNSAFE_getAllByType(TextInput);
    fireEvent.changeText(inputs[0], "new_user");
    fireEvent.changeText(inputs[1], "new@example.com");
    fireEvent.changeText(inputs[2], "password123");
    fireEvent.press(screen.getByText("Submit"));

    await waitFor(() => {
      expect(alertMock).toHaveBeenCalledWith("Error", "Failed to create user. Please try again.");
    });
  });

  it("shows unexpected error message for non-axios failures", async () => {
    mockedCreateUser.mockRejectedValue(new Error("boom"));
    mockedIsAxiosError.mockReturnValue(false);

    render(<CreateUserPage />);

    const inputs = screen.UNSAFE_getAllByType(TextInput);
    fireEvent.changeText(inputs[0], "new_user");
    fireEvent.changeText(inputs[1], "new@example.com");
    fireEvent.changeText(inputs[2], "password123");
    fireEvent.press(screen.getByText("Submit"));

    await waitFor(() => {
      expect(alertMock).toHaveBeenCalledWith(
        "Error",
        "An unexpected error occurred. Please try again.",
      );
    });
  });

  it("shows error for axios error with no response (network failure)", async () => {
    const networkError = {
      message: "Network error",
      isAxiosError: true,
      response: null,
      status: undefined,
    };
    mockedCreateUser.mockRejectedValue(networkError);
    mockedIsAxiosError.mockReturnValue(true);

    render(<CreateUserPage />);

    const inputs = screen.UNSAFE_getAllByType(TextInput);
    fireEvent.changeText(inputs[0], "new_user");
    fireEvent.changeText(inputs[1], "new@example.com");
    fireEvent.changeText(inputs[2], "password123");
    fireEvent.press(screen.getByText("Submit"));

    await waitFor(() => {
      // When there's no response and no status, it falls through to the generic error
      expect(alertMock).toHaveBeenCalledWith("Error", "Failed to create user. Please try again.");
    });
  });

  it("shows error for axios error with response object", async () => {
    const axiosErrorWithResponse = {
      message: "Request failed",
      isAxiosError: true,
      response: {
        status: 503,
        data: { error: "Service unavailable" },
      },
      status: 503,
    };
    mockedCreateUser.mockRejectedValue(axiosErrorWithResponse);
    mockedIsAxiosError.mockReturnValue(true);

    render(<CreateUserPage />);

    const inputs = screen.UNSAFE_getAllByType(TextInput);
    fireEvent.changeText(inputs[0], "new_user");
    fireEvent.changeText(inputs[1], "new@example.com");
    fireEvent.changeText(inputs[2], "password123");
    fireEvent.press(screen.getByText("Submit"));

    await waitFor(() => {
      // When there's a response but unknown status code
      expect(alertMock).toHaveBeenCalledWith("Error", "Failed to create user. Please try again.");
    });
  });

  it("navigates back to login when back button is pressed", () => {
    render(<CreateUserPage />);

    fireEvent.press(screen.getByText("Back to Login page"));

    expect(navigateMock).toHaveBeenCalledWith("/loginPage");
  });
});

