import React from "react";
import { Alert, Image } from "react-native";
import { fireEvent, render, screen, waitFor } from "@testing-library/react-native";
import AllRecipePage from "../screens/allRecipePage";
import { getAllRecipes } from "../api/recipe";
import { router } from "expo-router";

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
  };
});

describe("AllRecipePage", () => {
  const mockedGetAllRecipes = getAllRecipes as jest.MockedFunction<typeof getAllRecipes>;
  const alertMock = jest.spyOn(Alert, "alert");
  const originalBackendUrl = process.env.EXPO_PUBLIC_BACKEND_URL;

  beforeEach(() => {
    jest.clearAllMocks();
    process.env.EXPO_PUBLIC_BACKEND_URL = "https://api.test/api";
  });

  afterEach(() => {
    process.env.EXPO_PUBLIC_BACKEND_URL = originalBackendUrl;
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

  it("normalizes relative and duplicated /api image paths", async () => {
    process.env.EXPO_PUBLIC_BACKEND_URL = "https://api.test/api";
    mockedGetAllRecipes.mockResolvedValue({
      recipes: [
        { id: 3, title: "Relative", image_url: "static\\images\\rel.png" },
        { id: 4, title: "Api Path", image_url: "/api/static/images/api.png" },
      ],
    } as any);

    render(<AllRecipePage />);

    await waitFor(() => {
      expect(screen.getByText("Relative")).toBeTruthy();
      expect(screen.getByText("Api Path")).toBeTruthy();
    });

    const recipeImages = screen.UNSAFE_getAllByType(Image);
    expect(recipeImages[0].props.source.uri).toContain("/static/images/rel.png");
    expect(recipeImages[1].props.source.uri).not.toContain("/api//api/");
    expect(recipeImages[1].props.source.uri).toContain("/static/images/api.png");
  });

  it("uses empty backend base when env variable is missing", async () => {
    delete process.env.EXPO_PUBLIC_BACKEND_URL;
    mockedGetAllRecipes.mockResolvedValue({
      recipes: [{ id: 9, title: "Envless", image_url: "relative/path.png" }],
    } as any);

    render(<AllRecipePage />);

    await waitFor(() => {
      expect(screen.getByText("Envless")).toBeTruthy();
    });

    const recipeImages = screen.UNSAFE_getAllByType(Image);
    expect(recipeImages[0].props.source.uri).toBe("/relative/path.png");
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

  it("handles malformed recipe payloads by surfacing an unknown fetch error", async () => {
    mockedGetAllRecipes.mockResolvedValue({ recipes: {} } as any);

    render(<AllRecipePage />);

    await waitFor(() => {
      expect(alertMock).toHaveBeenCalledWith("Error: Unknown", expect.stringContaining("map"));
    });
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
