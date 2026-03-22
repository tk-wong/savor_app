import React from "react";
import { render, screen } from "@testing-library/react-native";
import { useFonts } from "expo-font";
import RootLayout from "../app/_layout";
import TabsLayout from "../app/(tabs)/_layout";
import IndexPage from "../app/index";
import LoginRoutePage from "../app/loginPage";
import CreateUserRoutePage from "../app/createUserPage";
import ChatHistoryRoutePage from "../app/chatHistoryPage";
import RecipeRoutePage from "../app/recipePage";
import TabChatRoutePage from "../app/(tabs)/chatPage";
import TabAllRecipesRoutePage from "../app/(tabs)/allRecipePage";

jest.mock("../screens/loginPage", () => {
  const React = require("react");
  const { Text } = require("react-native");
  return () => <Text>Mock Login Screen</Text>;
});

jest.mock("../screens/createUserPage", () => {
  const React = require("react");
  const { Text } = require("react-native");
  return () => <Text>Mock Create User Screen</Text>;
});

jest.mock("../screens/chatHistoryPage", () => {
  const React = require("react");
  const { Text } = require("react-native");
  return () => <Text>Mock Chat History Screen</Text>;
});

jest.mock("../screens/recipePage", () => {
  const React = require("react");
  const { Text } = require("react-native");
  return () => <Text>Mock Recipe Screen</Text>;
});

jest.mock("../screens/chatPage", () => {
  const React = require("react");
  const { Text } = require("react-native");
  return () => <Text>Mock Chat Screen</Text>;
});

jest.mock("../screens/allRecipePage", () => {
  const React = require("react");
  const { Text } = require("react-native");
  return () => <Text>Mock All Recipes Screen</Text>;
});

jest.mock("expo-font", () => ({
  useFonts: jest.fn(),
}));

jest.mock("@expo-google-fonts/inter", () => ({
  Inter_400Regular: "Inter_400Regular",
  Inter_400Regular_Italic: "Inter_400Regular_Italic",
  Inter_700Bold: "Inter_700Bold",
  Inter_700Bold_Italic: "Inter_700Bold_Italic",
}));

jest.mock("@expo/vector-icons", () => ({
  Ionicons: () => null,
}));

jest.mock("expo-router", () => {
  const React = require("react");
  const { Text, View } = require("react-native");

  const Stack = ({ children }: { children?: React.ReactNode }) => <View>{children}<Text>Mock Stack</Text></View>;
  Stack.Screen = ({ name }: { name: string }) => <Text>{`StackScreen:${name}`}</Text>;

  const Tabs = ({ children }: { children?: React.ReactNode }) => <View>{children}<Text>Mock Tabs</Text></View>;
  Tabs.Screen = ({ name }: { name: string }) => <Text>{`TabsScreen:${name}`}</Text>;

  return { Stack, Tabs };
});

describe("App route pages (excluding testing pages)", () => {
  const mockedUseFonts = useFonts as jest.Mock;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders root layout stack once fonts are loaded", () => {
    mockedUseFonts.mockReturnValue([true, null]);

    render(<RootLayout />);

    expect(screen.getByText("Mock Stack")).toBeTruthy();
    expect(screen.getByText("StackScreen:loginPage")).toBeTruthy();
    expect(screen.getByText("StackScreen:(tabs)")).toBeTruthy();
  });

  it("returns null in root layout while fonts are loading", () => {
    mockedUseFonts.mockReturnValue([false, null]);

    const rendered = render(<RootLayout />);

    expect(rendered.toJSON()).toBeNull();
  });

  it("renders root layout and logs when font loading returns an error", () => {
    const fontError = new Error("font load failure");
    mockedUseFonts.mockReturnValue([false, fontError]);

    render(<RootLayout />);

    expect(screen.getByText("Mock Stack")).toBeTruthy();
    expect(console.error).toHaveBeenCalledWith("Cannot load font", fontError);
  });

  it("renders tabs layout screens", () => {
    render(<TabsLayout />);

    expect(screen.getByText("Mock Tabs")).toBeTruthy();
    expect(screen.getByText("TabsScreen:chatPage")).toBeTruthy();
    expect(screen.getByText("TabsScreen:allRecipePage")).toBeTruthy();
  });

  it("renders app index and non-testing route wrappers", () => {
    render(<IndexPage />);
    expect(screen.getByText("Mock Login Screen")).toBeTruthy();

    render(<LoginRoutePage />);
    expect(screen.getAllByText("Mock Login Screen").length).toBeGreaterThan(0);

    render(<CreateUserRoutePage />);
    expect(screen.getByText("Mock Create User Screen")).toBeTruthy();

    render(<ChatHistoryRoutePage />);
    expect(screen.getByText("Mock Chat History Screen")).toBeTruthy();

    render(<RecipeRoutePage />);
    expect(screen.getByText("Mock Recipe Screen")).toBeTruthy();

    render(<TabChatRoutePage />);
    expect(screen.getByText("Mock Chat Screen")).toBeTruthy();

    render(<TabAllRecipesRoutePage />);
    expect(screen.getByText("Mock All Recipes Screen")).toBeTruthy();
  });
});

