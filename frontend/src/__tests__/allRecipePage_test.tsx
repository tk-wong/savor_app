import React from "react";
import { Alert, Image, Platform, View } from "react-native";
import { fireEvent, render, screen, waitFor } from "@testing-library/react-native";
import AllRecipePage from "../screens/allRecipePage";
import { getAllRecipes } from "../api/recipe";
import { router } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";

jest.mock("../api/recipe", () => ({
  getAllRecipes: jest.fn(),
}));

jest.mock("expo-router", () => ({
  router: {
    push: jest.fn(),
  },
  useFocusEffect: (effect: () => void) => {
    const React = require("react");
    React.useEffect(() => {
      effect();
    }, [effect]);
  },
  Stack: {
    Screen: () => null,
  },
}));

jest.mock("@react-navigation/elements", () => ({
  useHeaderHeight: jest.fn(() => 56),
}));

jest.mock("react-native-safe-area-context", () => {
  const { View } = require("react-native");
  return {
    SafeAreaView: ({ children }: { children: React.ReactNode }) => <View>{children}</View>,
    useSafeAreaInsets: jest.fn(() => ({ top: 0, right: 0, bottom: 0, left: 0 })),
  };
});

describe("AllRecipePage", () => {
  const mockedGetAllRecipes = getAllRecipes as jest.MockedFunction<typeof getAllRecipes>;
  const mockedUseSafeAreaInsets = useSafeAreaInsets as jest.Mock;
  const alertMock = jest.spyOn(Alert, "alert");
  const originalPlatformOS = Platform.OS;

  beforeEach(() => {
    jest.clearAllMocks();
    mockedUseSafeAreaInsets.mockReturnValue({ top: 0, right: 0, bottom: 0, left: 0 });
    Object.defineProperty(Platform, "OS", { configurable: true, value: originalPlatformOS });
  });

  afterEach(() => {
    Object.defineProperty(Platform, "OS", { configurable: true, value: originalPlatformOS });
  });

  it("fetches and renders recipes, including placeholder image fallback", async () => {
    mockedGetAllRecipes.mockResolvedValue({
      recipes: [
        { id: 1, title: "Tomato Soup", image_url: "https://cdn.test/soup.png" },
        { id: 2, title: "Garden Salad", image_url: null },
      ],
    } as any);

    render(<AllRecipePage />);

    await waitFor(() => {
      expect(screen.getByText("Tomato Soup")).toBeTruthy();
      expect(screen.getByText("Garden Salad")).toBeTruthy();
    });

    const recipeImages = screen.UNSAFE_getAllByType(Image);
    expect(recipeImages[0].props.source).toEqual({ uri: "https://cdn.test/soup.png" });
    expect(recipeImages[1].props.source).toEqual({
      uri: "https://blocks.astratic.com/img/general-img-landscape.png",
    });
  });

  it("navigates to recipe page when a recipe is pressed", async () => {
    mockedGetAllRecipes.mockResolvedValue({
      recipes: [{ id: 101, title: "Pasta", image_url: "https://cdn.test/pasta.png" }],
    } as any);

    render(<AllRecipePage />);

    await waitFor(() => {
      expect(screen.getByText("Pasta")).toBeTruthy();
    });

    fireEvent.press(screen.getByText("Pasta"));

    expect(router.push).toHaveBeenCalledWith({ pathname: "/recipePage", params: { id: 101 } });
  });

  it("shows an alert when fetching recipes fails", async () => {
    mockedGetAllRecipes.mockRejectedValue({ status: 500, message: "Failed to load recipes" });

    render(<AllRecipePage />);

    await waitFor(() => {
      expect(alertMock).toHaveBeenCalledWith("Error: 500", "Failed to load recipes");
    });
  });

  it("renders android bottom spacer using safe-area inset", async () => {
    Object.defineProperty(Platform, "OS", { configurable: true, value: "android" });
    mockedUseSafeAreaInsets.mockReturnValue({ top: 0, right: 0, bottom: 24, left: 0 });
    mockedGetAllRecipes.mockResolvedValue({ recipes: [] } as any);

    render(<AllRecipePage />);

    await waitFor(() => {
      expect(mockedGetAllRecipes).toHaveBeenCalled();
    });

    const spacerExists = screen.UNSAFE_getAllByType(View).some((node) => {
      const style = node.props.style;
      if (Array.isArray(style)) return style.some((s) => s?.height === 24);
      return style?.height === 24;
    });

    expect(spacerExists).toBe(true);
  });

  it("shows default unknown error details when request rejects without status/message", async () => {
    mockedGetAllRecipes.mockRejectedValue({});

    render(<AllRecipePage />);

    await waitFor(() => {
      expect(alertMock).toHaveBeenCalledWith(
        "Error: Unknown",
        "Unknown error occurred while fetching all recipes.",
      );
    });
  });
});
