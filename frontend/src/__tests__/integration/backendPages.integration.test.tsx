import React from "react";
import { Alert, TextInput } from "react-native";
import { fireEvent, render, screen, waitFor } from "@testing-library/react-native";
import * as authApi from "../../api/auth";
import { getAllRecipes, getRecipeById } from "../../api/recipe";
import { getAllChatGroups, getNewChatGroup, sendMessage } from "../../api/chat";
import LoginPage from "../../screens/loginPage";
import CreateUserPage from "../../screens/createUserPage";
import AllRecipePage from "../../screens/allRecipePage";
import RecipePage from "../../screens/recipePage";
import ChatHistoryPage from "../../screens/chatHistoryPage";
import ChatPage from "../../screens/chatPage";

const mockPush = jest.fn();
const mockNavigate = jest.fn();
const mockBack = jest.fn();
let mockSearchParams: Record<string, unknown> = {};

jest.mock("expo-router", () => {
  const ReactLocal = require("react");
  const { Text, View } = require("react-native");

  const Stack = ({ children }: { children?: React.ReactNode }) => ReactLocal.createElement(View, null, children);
  Stack.Screen = () => null;

  const Tabs = ({ children }: { children?: React.ReactNode }) => ReactLocal.createElement(View, null, children);
  Tabs.Screen = ({ name }: { name: string }) => ReactLocal.createElement(Text, null, `TabsScreen:${name}`);

  return {
    router: {
      push: (...args: unknown[]) => mockPush(...args),
      navigate: (...args: unknown[]) => mockNavigate(...args),
      back: (...args: unknown[]) => mockBack(...args),
    },
    useRouter: () => ({
      push: (...args: unknown[]) => mockPush(...args),
      navigate: (...args: unknown[]) => mockNavigate(...args),
      back: (...args: unknown[]) => mockBack(...args),
    }),
    useLocalSearchParams: () => mockSearchParams,
    useFocusEffect: (effect: () => void) => {
      ReactLocal.useEffect(() => {
        effect();
      }, [effect]);
    },
    Stack,
    Tabs,
  };
});

jest.mock("expo-secure-store", () => {
  const store = new Map<string, string>();
  return {
    setItemAsync: jest.fn(async (key: string, value: string) => {
      store.set(key, value);
    }),
    getItemAsync: jest.fn(async (key: string) => store.get(key) ?? null),
    deleteItemAsync: jest.fn(async (key: string) => {
      store.delete(key);
    }),
  };
});

jest.mock("react-native-safe-area-context", () => {
  const ReactLocal = require("react");
  const { View } = require("react-native");
  return {
    SafeAreaView: ({ children }: { children: React.ReactNode }) => ReactLocal.createElement(View, null, children),
    useSafeAreaInsets: () => ({ top: 0, right: 0, bottom: 0, left: 0 }),
  };
});

jest.mock("@react-navigation/elements", () => ({
  useHeaderHeight: () => 56,
}));

jest.mock("nativewind", () => ({
  cssInterop: jest.fn(),
}));

jest.mock("@expo/vector-icons", () => ({
  Feather: ({ onPress, name }: { onPress?: () => void; name: string }) => {
    const ReactLocal = require("react");
    const { Pressable, Text } = require("react-native");
    return ReactLocal.createElement(
      Pressable,
      { testID: `feather-${name}`, onPress },
      ReactLocal.createElement(Text, null, name),
    );
  },
  Ionicons: () => null,
}));

jest.mock("@expo/vector-icons/AntDesign", () => ({
  __esModule: true,
  default: ({ onPress, name, accessibilityHint }: { onPress?: () => void; name: string; accessibilityHint?: string }) => {
    const ReactLocal = require("react");
    const { Pressable, Text } = require("react-native");
    return ReactLocal.createElement(
      Pressable,
      { testID: `ant-${name}`, accessibilityHint, onPress },
      ReactLocal.createElement(Text, null, name),
    );
  },
}));

jest.mock("@react-native-vector-icons/material-design-icons", () => ({
  MaterialDesignIcons: ({ onPress, name, accessibilityHint }: { onPress?: () => void; name: string; accessibilityHint?: string }) => {
    const ReactLocal = require("react");
    const { Pressable, Text } = require("react-native");
    return ReactLocal.createElement(
      Pressable,
      { testID: `mdi-${name}`, accessibilityHint, onPress },
      ReactLocal.createElement(Text, null, name),
    );
  },
}));

jest.mock("react-native-markdown-display", () => {
  const ReactLocal = require("react");
  const { Text } = require("react-native");
  return ({ children }: { children: React.ReactNode }) => ReactLocal.createElement(Text, null, children);
});

jest.mock("expo-speech-recognition", () => ({
  ExpoSpeechRecognitionModule: {
    requestPermissionsAsync: jest.fn(async () => ({ granted: true })),
    start: jest.fn(),
    stop: jest.fn(),
  },
  useSpeechRecognitionEvent: jest.fn(),
}));

jest.mock("../../hooks/useTextToSpeech", () => ({
  useTextToSpeech: () => ({
    speak: jest.fn(async () => undefined),
    stopSpeaking: jest.fn(async () => undefined),
  }),
}));

jest.mock("../../hooks/useSpeechToText", () => ({
  useSpeechToText: () => ({
    startListening: jest.fn(),
    stopListening: jest.fn(),
  }),
}));

let latestGiftedProps: any = null;

jest.mock("react-native-gifted-chat", () => {
  const ReactLocal = require("react");
  const { Pressable, Text, View } = require("react-native");

  const GiftedChat = (props: any) => {
    latestGiftedProps = props;
    return ReactLocal.createElement(
      View,
      { testID: "gifted-chat" },
      ReactLocal.createElement(
        Pressable,
        {
          testID: "gifted-send-button",
          onPress: () =>
            props.onSend?.([
              {
                _id: "integration-msg",
                text: "integration hello",
                createdAt: new Date(),
                user: { _id: 1, name: "Integration User" },
              },
            ]),
        },
        ReactLocal.createElement(Text, null, "send"),
      ),
      ReactLocal.createElement(Text, { testID: "gifted-message-count" }, String(props.messages?.length ?? 0)),
      props.renderActions ? ReactLocal.createElement(props.renderActions, {}) : null,
    );
  };

  (GiftedChat as any).append = (previousMessages: any[], nextMessages: any[]) => [
    ...nextMessages,
    ...previousMessages,
  ];

  return {
    GiftedChat,
    Actions: ({ icon }: { icon?: () => React.ReactNode }) => ReactLocal.createElement(View, null, icon?.()),
    Bubble: () => ReactLocal.createElement(View, null),
    Day: () => ReactLocal.createElement(View, null),
    Send: ({ children }: { children?: React.ReactNode }) => ReactLocal.createElement(View, null, children),
  };
});

const backendUrl = process.env.EXPO_PUBLIC_BACKEND_URL;
const canRunBackendSuite = Boolean(backendUrl);
const describeBackend = canRunBackendSuite ? describe : describe.skip;

describeBackend("Backend integration for non-testing screens", () => {
  jest.setTimeout(180000);

  const alertSpy = jest.spyOn(Alert, "alert").mockImplementation(() => {});
  const uniqueSuffix = `${Date.now()}-${Math.floor(Math.random() * 100000)}`;
  const integrationUser = {
    username: `integration-${uniqueSuffix}`,
    email: `integration-${uniqueSuffix}@example.com`,
    password: "Integration123!",
  };

  beforeAll(async () => {
    await authApi.createUser(integrationUser.email, integrationUser.username, integrationUser.password);
    await authApi.login(integrationUser.email, integrationUser.password);
  });

  beforeEach(() => {
    jest.clearAllMocks();
    latestGiftedProps = null;
    mockSearchParams = {};
  });

  afterAll(() => {
    alertSpy.mockRestore();
  });

  it("logs in from login page with backend credentials", async () => {
    render(<LoginPage />);

    fireEvent.changeText(screen.getByPlaceholderText("Enter your email"), integrationUser.email);
    fireEvent.changeText(screen.getByPlaceholderText("Enter your password"), integrationUser.password);
    fireEvent.press(screen.getByText("Submit"));

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith("/chatPage");
    });
  });

  it("creates a user from create user page", async () => {
    const randomSuffix = `${Date.now()}-${Math.floor(Math.random() * 10000)}`;
    const username = `integration-${randomSuffix}`;
    const email = `integration-${randomSuffix}@example.com`;
    const password = "Integration123!";

    render(<CreateUserPage />);

    const inputs = screen.UNSAFE_getAllByType(TextInput);
    fireEvent.changeText(inputs[0], username);
    fireEvent.changeText(inputs[1], email);
    fireEvent.changeText(inputs[2], password);
    fireEvent.press(screen.getByText("Submit"));

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith("/loginPage");
    });
  });

  it("loads all recipe page data from backend", async () => {
    const recipeResponse = await getAllRecipes();
    const rendered = render(<AllRecipePage />);

    if (recipeResponse.recipes.length > 0) {
      await waitFor(() => {
        expect(screen.getByText(recipeResponse.recipes[0].title)).toBeTruthy();
      });
    } else {
      expect(rendered.toJSON()).not.toBeNull();
    }
  });

  it("loads a backend recipe in recipe page", async () => {
    const allRecipes = await getAllRecipes();
    if (allRecipes.recipes.length === 0) {
      return;
    }

    const targetRecipeId = allRecipes.recipes[0].id;
    const detail = await getRecipeById(targetRecipeId);
    mockSearchParams = { id: String(targetRecipeId) };

    render(<RecipePage />);

    await waitFor(() => {
      expect(screen.getByText(detail.recipe.description)).toBeTruthy();
    });
  });

  it("loads chat history page from backend", async () => {
    const newGroup = await getNewChatGroup();
    await sendMessage("integration history seed", newGroup.group_id);
    const groups = await getAllChatGroups();

    const rendered = render(<ChatHistoryPage />);

    expect(Array.isArray(groups.chat_groups)).toBe(true);
    expect(rendered.toJSON()).not.toBeNull();

    if (groups.chat_groups.length > 0) {
      const seededGroup = groups.chat_groups.find((group) => group.id === newGroup.group_id);
      expect(seededGroup).toBeTruthy();
    }
  });

  it("sends a chat message through chat page to backend", async () => {
    render(<ChatPage />);

    fireEvent.press(screen.getByTestId("gifted-send-button"));

    await waitFor(
      () => {
        expect(Number(screen.getByTestId("gifted-message-count").props.children)).toBeGreaterThan(0);
      },
      { timeout: 20000 },
    );
  });
});

if (!canRunBackendSuite) {
  describe("Backend integration for non-testing screens", () => {
    it("requires EXPO_PUBLIC_BACKEND_URL", () => {
      expect(canRunBackendSuite).toBe(false);
    });
  });
}
