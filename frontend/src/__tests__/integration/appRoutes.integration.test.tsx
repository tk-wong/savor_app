import React from "react";
import { render, screen } from "@testing-library/react-native";
import { useFonts } from "expo-font";
import RootLayout from "../../app/_layout";
import TabsLayout from "../../app/(tabs)/_layout";
import IndexPage from "../../app/index";
import LoginRoutePage from "../../app/loginPage";
import CreateUserRoutePage from "../../app/createUserPage";
import ChatHistoryRoutePage from "../../app/chatHistoryPage";
import RecipeRoutePage from "../../app/recipePage";
import TabChatRoutePage from "../../app/(tabs)/chatPage";
import TabAllRecipeRoutePage from "../../app/(tabs)/allRecipePage";
import LoginScreen from "../../screens/loginPage";
import CreateUserScreen from "../../screens/createUserPage";
import ChatHistoryScreen from "../../screens/chatHistoryPage";
import RecipeScreen from "../../screens/recipePage";
import ChatScreen from "../../screens/chatPage";
import AllRecipeScreen from "../../screens/allRecipePage";

jest.mock("../../screens/loginPage", () => {
  const ReactLocal = require("react");
  const { Text } = require("react-native");
  return () => ReactLocal.createElement(Text, null, "Login Screen");
});

jest.mock("../../screens/createUserPage", () => {
  const ReactLocal = require("react");
  const { Text } = require("react-native");
  return () => ReactLocal.createElement(Text, null, "Create User Screen");
});

jest.mock("../../screens/chatHistoryPage", () => {
  const ReactLocal = require("react");
  const { Text } = require("react-native");
  return () => ReactLocal.createElement(Text, null, "Chat History Screen");
});

jest.mock("../../screens/recipePage", () => {
  const ReactLocal = require("react");
  const { Text } = require("react-native");
  return () => ReactLocal.createElement(Text, null, "Recipe Screen");
});

jest.mock("../../screens/chatPage", () => {
  const ReactLocal = require("react");
  const { Text } = require("react-native");
  return () => ReactLocal.createElement(Text, null, "Chat Screen");
});

jest.mock("../../screens/allRecipePage", () => {
  const ReactLocal = require("react");
  const { Text } = require("react-native");
  return () => ReactLocal.createElement(Text, null, "All Recipe Screen");
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
  const ReactLocal = require("react");
  const { Text, View } = require("react-native");

  const Stack = ({ children }: { children?: React.ReactNode }) => ReactLocal.createElement(View, null, children);
  Stack.Screen = ({ name }: { name: string }) => ReactLocal.createElement(Text, null, `StackScreen:${name}`);

  const Tabs = ({ children }: { children?: React.ReactNode }) => ReactLocal.createElement(View, null, children);
  Tabs.Screen = ({ name }: { name: string }) => ReactLocal.createElement(Text, null, `TabsScreen:${name}`);

  return { Stack, Tabs };
});

describe("Integration route coverage for non-testing app pages", () => {
  const mockedUseFonts = useFonts as jest.Mock;

  beforeEach(() => {
    jest.clearAllMocks();
    mockedUseFonts.mockReturnValue([true, null]);
  });

  it("renders root and tabs layouts", () => {
    render(<RootLayout />);
    expect(screen.getByText("StackScreen:loginPage")).toBeTruthy();
    expect(screen.getByText("StackScreen:(tabs)")).toBeTruthy();

    render(<TabsLayout />);
    expect(screen.getByText("TabsScreen:chatPage")).toBeTruthy();
    expect(screen.getByText("TabsScreen:allRecipePage")).toBeTruthy();
  });

  it("routes index and wrappers to the non-testing screens", () => {
    render(<IndexPage />);
    expect(screen.getByText("Login Screen")).toBeTruthy();

    render(<LoginRoutePage />);
    expect(screen.getByText("Login Screen")).toBeTruthy();

    render(<CreateUserRoutePage />);
    expect(screen.getByText("Create User Screen")).toBeTruthy();

    render(<ChatHistoryRoutePage />);
    expect(screen.getByText("Chat History Screen")).toBeTruthy();

    render(<RecipeRoutePage />);
    expect(screen.getByText("Recipe Screen")).toBeTruthy();

    render(<TabChatRoutePage />);
    expect(screen.getByText("Chat Screen")).toBeTruthy();

    render(<TabAllRecipeRoutePage />);
    expect(screen.getByText("All Recipe Screen")).toBeTruthy();
  });

  it("keeps wrapper exports aligned with each screen module", () => {
    expect(LoginRoutePage).toBe(LoginScreen);
    expect(CreateUserRoutePage).toBe(CreateUserScreen);
    expect(ChatHistoryRoutePage).toBe(ChatHistoryScreen);
    expect(RecipeRoutePage).toBe(RecipeScreen);
    expect(TabChatRoutePage).toBe(ChatScreen);
    expect(TabAllRecipeRoutePage).toBe(AllRecipeScreen);
  });
});
