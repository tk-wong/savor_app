import React from "react";
import { Alert, Platform, useColorScheme, View } from "react-native";
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react-native";
import ChatPage, { renderSend } from "../screens/chatPage";
import { getChatHistoryByGroupId, getNewChatGroup, sendMessage } from "../api/chat";
import { useTextToSpeech } from "../hooks/useTextToSpeech";
import { useLocalSearchParams, useRouter } from "expo-router";
import { ExpoSpeechRecognitionModule } from "expo-speech-recognition";

jest.mock("nativewind", () => ({
  cssInterop: jest.fn(),
}));

jest.mock("../api/chat", () => ({
  getChatHistoryByGroupId: jest.fn(),
  getNewChatGroup: jest.fn(),
  sendMessage: jest.fn(),
}));

jest.mock("../hooks/useTextToSpeech", () => ({
  useTextToSpeech: jest.fn(),
}));

jest.mock("@react-navigation/elements", () => ({
  useHeaderHeight: jest.fn(() => 50),
}));

jest.mock("react-native-safe-area-context", () => ({
  useSafeAreaInsets: jest.fn(() => ({ top: 0, right: 0, bottom: 8, left: 0 })),
}));

jest.mock("expo-router", () => ({
  useRouter: jest.fn(),
  useLocalSearchParams: jest.fn(),
  useFocusEffect: (effect: () => void) => {
    const ReactLocal = require("react");
    ReactLocal.useEffect(() => {
      effect();
    }, [effect]);
  },
}));

const mockSpeechCallbacks: Record<string, (event: any) => void> = {};
const mockRequestPermissionsAsync = jest.fn();
const mockStart = jest.fn();
const mockStop = jest.fn();

jest.mock("expo-speech-recognition", () => ({
  ExpoSpeechRecognitionModule: {
    requestPermissionsAsync: (...args: unknown[]) => mockRequestPermissionsAsync(...args),
    start: (...args: unknown[]) => mockStart(...args),
    stop: (...args: unknown[]) => mockStop(...args),
  },
  useSpeechRecognitionEvent: (eventName: string, callback: (event: any) => void) => {
    mockSpeechCallbacks[eventName] = callback;
  },
}));

jest.mock("react-native-markdown-display", () => {
  const ReactLocal = require("react");
  const { Text } = require("react-native");
  return ({ children, style }: { children: React.ReactNode; style?: any }) =>
      ReactLocal.createElement(Text, { testID: "markdown", style: style?.body }, children);
});

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

jest.mock("../components/styledHeader", () => ({
  StyledHeader: ({ options }: { options?: { headerRight?: () => React.ReactNode } }) => {
    const ReactLocal = require("react");
    const { View } = require("react-native");
    return ReactLocal.createElement(View, { testID: "styled-header" }, options?.headerRight?.());
  },
}));

let mockLatestGiftedChatProps: any = null;

jest.mock("react-native-gifted-chat", () => {
  const ReactLocal = require("react");
  const { Pressable, Text, View } = require("react-native");

  const GiftedChat = (props: any) => {
    mockLatestGiftedChatProps = props;
    const sendTrimmed = ReactLocal.createElement(
        Pressable,
        {
          testID: "gifted-send-trimmed",
          onPress: () =>
              props.onSend?.([
                {
                  _id: "trimmed",
                  text: "  hello bot!  ",
                  createdAt: new Date(),
                  user: { _id: 1, name: "User" },
                },
              ]),
        },
        ReactLocal.createElement(Text, null, "send-trimmed"),
    );
    const sendEmpty = ReactLocal.createElement(
        Pressable,
        {
          testID: "gifted-send-empty",
          onPress: () =>
              props.onSend?.([
                {
                  _id: "empty",
                  text: "   ",
                  createdAt: new Date(),
                  user: { _id: 1, name: "User" },
                },
              ]),
        },
        ReactLocal.createElement(Text, null, "send-empty"),
    );
    const sendNone = ReactLocal.createElement(
        Pressable,
        { testID: "gifted-send-none", onPress: () => props.onSend?.([]) },
        ReactLocal.createElement(Text, null, "send-none"),
    );
    const sendUndefined = ReactLocal.createElement(
        Pressable,
        { testID: "gifted-send-undefined", onPress: () => props.onSend?.(undefined) },
        ReactLocal.createElement(Text, null, "send-undefined"),
    );
    const sendNoArg = ReactLocal.createElement(
        Pressable,
        { testID: "gifted-send-noarg", onPress: () => props.onSend?.() },
        ReactLocal.createElement(Text, null, "send-noarg"),
    );

    return ReactLocal.createElement(
        View,
        { testID: "gifted-chat" },
        sendTrimmed,
        sendEmpty,
        sendNone,
        sendUndefined,
        sendNoArg,
        props.renderActions ? ReactLocal.createElement(props.renderActions, {}) : null,
        props.renderMessageText?.({
          currentMessage: { _id: 1, text: "**hello**", createdAt: new Date(), user: { _id: 1 } },
        }),
        props.renderMessageText?.({
          currentMessage: { _id: 2, text: "bot text", createdAt: new Date(), user: { _id: "bot" } },
        }),
        ReactLocal.createElement(View, { testID: "render-message-empty" }, props.renderMessageText?.({})),
        ReactLocal.createElement(View, { testID: "render-bubble" }, props.renderBubble?.({})),
        ReactLocal.createElement(View, { testID: "render-day" }, props.renderDay?.({})),
    );
  };

  (GiftedChat as any).append = (previousMessages: any[], nextMessages: any[]) => [...nextMessages, ...previousMessages];

  return {
    GiftedChat,
    Actions: ({ icon }: { icon?: () => React.ReactNode }) =>
        ReactLocal.createElement(View, { testID: "actions" }, icon?.()),
    Bubble: ({ wrapperStyle }: { wrapperStyle?: any }) =>
        ReactLocal.createElement(
            View,
            { testID: "bubble" },
            ReactLocal.createElement(Text, null, JSON.stringify(wrapperStyle ?? {})),
        ),
    Day: ({ wrapperStyle, textProps }: { wrapperStyle?: any; textProps?: any }) =>
        ReactLocal.createElement(
            View,
            { testID: "day" },
            ReactLocal.createElement(Text, null, JSON.stringify({ wrapperStyle, textProps })),
        ),
    Send: ({ children, containerStyle, textStyle }: any) =>
        ReactLocal.createElement(
            View,
            { testID: "send", style: containerStyle },
            ReactLocal.createElement(Text, { testID: "send-text-style" }, JSON.stringify(textStyle)),
            children,
        ),
  };
});

describe("ChatPage", () => {
  const mockedGetChatHistoryByGroupId = getChatHistoryByGroupId as jest.MockedFunction<typeof getChatHistoryByGroupId>;
  const mockedGetNewChatGroup = getNewChatGroup as jest.MockedFunction<typeof getNewChatGroup>;
  const mockedSendMessage = sendMessage as jest.MockedFunction<typeof sendMessage>;
  const mockedUseTextToSpeech = useTextToSpeech as jest.Mock;
  const mockedUseRouter = useRouter as jest.Mock;
  const mockedUseLocalSearchParams = useLocalSearchParams as jest.Mock;
  const mockedUseColorScheme = useColorScheme as jest.Mock;

  const speakMock = jest.fn().mockResolvedValue(undefined);
  const navigateMock = jest.fn();
  const alertMock = jest.spyOn(Alert, "alert");
  const warnMock = jest.spyOn(console, "warn").mockImplementation(() => {});
  const logMock = jest.spyOn(console, "log").mockImplementation(() => {});
  const originalPlatformOS = Platform.OS;
  const originalBackendUrl = process.env.EXPO_PUBLIC_BACKEND_URL;

  const triggerSpeechResult = (transcript?: string) => {
    mockSpeechCallbacks.result?.({
      results: transcript ? [{ transcript }] : [{}],
    });
  };

  beforeEach(() => {
    jest.clearAllMocks();
    Object.keys(mockSpeechCallbacks).forEach((key) => {
      delete mockSpeechCallbacks[key];
    });
    mockLatestGiftedChatProps = null;
    mockedUseTextToSpeech.mockReturnValue({ speak: speakMock });
    mockedUseRouter.mockReturnValue({ navigate: navigateMock });
    mockedUseLocalSearchParams.mockReturnValue({});
    mockedUseColorScheme.mockReturnValue("light");
    mockedGetNewChatGroup.mockResolvedValue({ group_id: 1 } as any);
    mockedSendMessage.mockResolvedValue({ prompt_type: "question", answer: "ok" } as any);
    mockRequestPermissionsAsync.mockResolvedValue({ granted: true });
    Object.defineProperty(Platform, "OS", { configurable: true, value: "ios" });
    process.env.EXPO_PUBLIC_BACKEND_URL = "https://api.test/api";
  });

  afterEach(() => {
    Object.defineProperty(Platform, "OS", { configurable: true, value: originalPlatformOS });
    process.env.EXPO_PUBLIC_BACKEND_URL = originalBackendUrl;
  });

  afterAll(() => {
    alertMock.mockRestore();
    warnMock.mockRestore();
    logMock.mockRestore();
  });

  it("loads history from params and renders header actions", async () => {
    mockedUseLocalSearchParams.mockReturnValue({ chatGroupId: "7" });
    mockedGetChatHistoryByGroupId.mockResolvedValue({
      chat_history: [
        { id: 2, prompt: "Second", response: "B", timestamp: "2026-01-02T00:00:00.000Z" },
        { id: 1, prompt: "First", response: "A", timestamp: "2026-01-01T00:00:00.000Z" },
      ],
    } as any);

    const firstRender = render(React.createElement(ChatPage));

    await waitFor(() => {
      expect(mockedGetChatHistoryByGroupId).toHaveBeenCalledWith(7);
    });
    await waitFor(() => {
      expect(mockLatestGiftedChatProps.messages).toHaveLength(4);
    });

    fireEvent.press(screen.getByTestId("ant-history"));
    expect(navigateMock).toHaveBeenCalledWith("/chatHistoryPage");

    fireEvent.press(screen.getByTestId("mdi-chat-plus-outline"));
    expect(mockLatestGiftedChatProps.messages).toEqual([]);
  });

  it("logs when no chat group param exists", () => {
    mockedUseLocalSearchParams.mockReturnValue({});

    const firstRender = render(React.createElement(ChatPage));

    expect(logMock).toHaveBeenCalledWith("No chat group ID in params, starting with new chat.");
  });

  it("creates a chat group and sends a question response after trimming input", async () => {
    mockedGetNewChatGroup.mockResolvedValue({ group_id: 42 } as any);
    mockedSendMessage.mockResolvedValue({ prompt_type: "question", answer: "Hello user" } as any);

    const firstRender = render(React.createElement(ChatPage));
    fireEvent.press(screen.getByTestId("gifted-send-trimmed"));

    await waitFor(() => {
      expect(mockedGetNewChatGroup).toHaveBeenCalled();
      expect(mockedSendMessage).toHaveBeenCalledWith("hello bot!", 42);
    });
    await waitFor(() => {
      expect(mockLatestGiftedChatProps.messages).toHaveLength(2);
    });
  });

  it("supports recipe responses and maps recipe image urls", async () => {
    mockedGetNewChatGroup.mockResolvedValue({ group_id: 55 } as any);
    mockedSendMessage.mockResolvedValue({
      prompt_type: "recipe",
      recipe: {
        id: 1,
        title: "Tomato Soup",
        description: "A cozy soup",
        ingredients: [{ ingredient_name: "Tomato", quantity: "2" }],
        directions: ["Boil", "Serve"],
        tips: ["Use ripe tomatoes"],
        image_url: "/api/static/images/soup.png",
      },
    } as any);

    const firstRender = render(React.createElement(ChatPage));
    fireEvent.press(screen.getByTestId("gifted-send-trimmed"));

    await waitFor(() => {
      expect(mockedSendMessage).toHaveBeenCalledWith("hello bot!", 55);
    });
    await waitFor(() => {
      expect(mockLatestGiftedChatProps.messages[0].image).toContain("/static/images/soup.png");
      expect(mockLatestGiftedChatProps.messages[0].text).toContain("Here's a recipe for you");
      expect(mockLatestGiftedChatProps.messages[0].text).toContain("1. Boil");
    });
  });

  it("handles invalid recipe payload from sendMessage and rolls back optimistic update", async () => {
    mockedGetNewChatGroup.mockResolvedValue({ group_id: 88 } as any);
    mockedSendMessage.mockResolvedValue({ prompt_type: "recipe", recipe: undefined } as any);

    render(React.createElement(ChatPage));
    fireEvent.press(screen.getByTestId("gifted-send-trimmed"));

    await waitFor(() => {
      expect(alertMock).toHaveBeenCalledWith(
          "Error",
          "Received invalid recipe data from server. Please try again.",
      );
    });
    expect(mockLatestGiftedChatProps.messages).toHaveLength(0);
  });

  it("formats recipe markdown fallbacks and image path variants", async () => {
    mockedGetNewChatGroup.mockResolvedValue({ group_id: 66 } as any);
    mockedSendMessage
        .mockResolvedValueOnce({
          prompt_type: "recipe",
          recipe: {
            id: 11,
            title: undefined,
            description: undefined,
            ingredients: [],
            directions: [],
            tips: [],
            image_url: "static\\images\\fallback.png",
          },
        } as any)
        .mockResolvedValueOnce({
          prompt_type: "recipe",
          recipe: {
            id: 12,
            title: "Mixed Ingredients",
            description: "Mixed",
            ingredients: [
              "Raw\\ntext",
              {},
              { ingredient_name: "Flour", quantity: "1 cup" },
              { ingredient_name: "Salt", quantity: "" },
              { ingredient_name: "", quantity: "2 tbsp" },
              { ingredient_name: "", quantity: "" },
            ],
            directions: ["Stir"],
            tips: ["Tip A"],
            image_url: "https://cdn.test/abs.png",
          },
        } as any);

    render(React.createElement(ChatPage));

    fireEvent.press(screen.getByTestId("gifted-send-trimmed"));
    await waitFor(() => {
      expect(mockLatestGiftedChatProps.messages[0].image).toContain("/static/images/fallback.png");
      expect(mockLatestGiftedChatProps.messages[0].text).toContain("- N/A");
      expect(mockLatestGiftedChatProps.messages[0].text).toContain("1. N/A");
    });

    fireEvent.press(screen.getByTestId("gifted-send-trimmed"));
    await waitFor(() => {
      const latestBotText = mockLatestGiftedChatProps.messages[0].text;
      expect(mockLatestGiftedChatProps.messages[0].image).toBe("https://cdn.test/abs.png");
      expect(latestBotText).toContain("- Raw\ntext");
      expect(latestBotText).toContain("- 1 cup Flour");
      expect(latestBotText).toContain("- Salt");
      expect(latestBotText).toContain("- 2 tbsp");
      expect(latestBotText).toContain("- N/A");
    });
  });

  it("parses stored history responses for question, recipe, and plain text fallbacks", async () => {
    mockedUseLocalSearchParams.mockReturnValue({ chatGroupId: "9" });
    mockedGetChatHistoryByGroupId.mockResolvedValue({
      chat_history: [
        {
          id: 1,
          prompt: "Q1",
          response: JSON.stringify({ prompt_type: "question", answer: "hello\\nworld" }),
          timestamp: "2026-01-01T00:00:00.000Z",
        },
        {
          id: 2,
          prompt: "Q2",
          response: JSON.stringify({
            prompt_type: "recipe",
            recipe: {
              id: 2,
              title: "Stored",
              description: "Stored desc",
              ingredients: [{ ingredient_name: "Egg", quantity: "1" }],
              directions: ["Cook"],
              tips: ["Serve"],
              image_url: "https://cdn.test/stored.png",
            },
          }),
          timestamp: "2026-01-01T00:00:01.000Z",
        },
        {
          id: 3,
          prompt: "Q3",
          response: JSON.stringify({ prompt_type: "recipe" }),
          timestamp: "2026-01-01T00:00:02.000Z",
          image_url: "https://cdn.test/fallback-image.png",
        },
        {
          id: 4,
          prompt: "Q4",
          response: "plain text",
          timestamp: "2026-01-01T00:00:03.000Z",
        },
      ],
    } as any);

    render(React.createElement(ChatPage));

    await waitFor(() => {
      expect(mockLatestGiftedChatProps.messages).toHaveLength(8);
    });

    const messageTexts = mockLatestGiftedChatProps.messages.map((m: any) => m.text);
    expect(messageTexts.join("\n")).toContain("hello\nworld");
    expect(messageTexts.join("\n")).toContain("## Stored");
    expect(messageTexts).toContain("");
    expect(messageTexts).toContain("plain text");

    const fallbackImageMessage = mockLatestGiftedChatProps.messages.find((m: any) => m._id === 3.5);
    expect(fallbackImageMessage?.image).toBe("https://cdn.test/fallback-image.png");
  });

  it("covers history parsing edge cases for malformed and object responses", async () => {
    delete process.env.EXPO_PUBLIC_BACKEND_URL;
    mockedUseLocalSearchParams.mockReturnValue({ chatGroupId: "12" });
    mockedGetChatHistoryByGroupId.mockResolvedValue({
      chat_history: [
        {
          id: 1,
          prompt: "empty answer",
          response: JSON.stringify({ prompt_type: "question", answer: "" }),
          timestamp: "2026-02-01T00:00:00.000Z",
        },
        {
          id: 2,
          prompt: "object response",
          response: { prompt_type: "recipe", recipe: { id: 2, title: "Obj", description: "D", ingredients: [{}], directions: [undefined], tips: [undefined], image_url: "static\\images\\obj.png" } },
          timestamp: "2026-02-01T00:00:01.000Z",
          image_url: "https://cdn.test/obj-fallback.png",
        },
        {
          id: 3,
          prompt: "broken json",
          response: "{not-json}",
          timestamp: "2026-02-01T00:00:02.000Z",
        },
        {
          id: 4,
          prompt: "object fallback",
          response: { foo: "bar" },
          timestamp: "2026-02-01T00:00:03.000Z",
        },
      ],
    } as any);

    render(React.createElement(ChatPage));

    await waitFor(() => {
      expect(mockLatestGiftedChatProps.messages).toHaveLength(8);
    });

    const textBlob = mockLatestGiftedChatProps.messages.map((m: any) => m.text).join("\n");
    expect(textBlob).toContain("## Obj");
    expect(textBlob).toContain("- N/A");
    expect(textBlob).toContain("1. ");
    expect(textBlob).toContain("{not-json}");
    expect(textBlob).toContain('{"foo":"bar"}');

    const historyRecipeImage = mockLatestGiftedChatProps.messages.find((m: any) => m._id === 2.5);
    expect(historyRecipeImage?.image).toContain("/static/images/");
  });

  it("uses empty history list when chat_history is not an array", async () => {
    mockedUseLocalSearchParams.mockReturnValue({ chatGroupId: "13" });
    mockedGetChatHistoryByGroupId.mockResolvedValue({ chat_history: {} } as any);

    render(React.createElement(ChatPage));

    await waitFor(() => {
      expect(mockLatestGiftedChatProps.messages).toEqual([]);
    });
  });

  it("returns undefined image for recipe messages without image_url", async () => {
    mockedGetNewChatGroup.mockResolvedValue({ group_id: 67 } as any);
    mockedSendMessage.mockResolvedValue({
      prompt_type: "recipe",
      recipe: {
        id: 67,
        title: "No Image",
        description: "desc",
        ingredients: [{ ingredient_name: "Egg", quantity: "1" }],
        directions: ["Cook"],
        tips: ["Serve"],
        image_url: undefined,
      },
    } as any);

    render(React.createElement(ChatPage));
    fireEvent.press(screen.getByTestId("gifted-send-trimmed"));

    await waitFor(() => {
      expect(mockLatestGiftedChatProps.messages[0].image).toBeUndefined();
    });
  });

  it("uses empty backend base fallback when env is missing", async () => {
    delete process.env.EXPO_PUBLIC_BACKEND_URL;
    mockedGetNewChatGroup.mockResolvedValue({ group_id: 91 } as any);
    mockedSendMessage.mockResolvedValue({
      prompt_type: "recipe",
      recipe: {
        id: 91,
        title: "Envless",
        description: "desc",
        ingredients: [{ ingredient_name: "X", quantity: "1" }],
        directions: ["Do"],
        tips: ["Tip"],
        image_url: "/api/static/images/envless.png",
      },
    } as any);

    render(React.createElement(ChatPage));
    fireEvent.press(screen.getByTestId("gifted-send-trimmed"));

    await waitFor(() => {
      expect(mockLatestGiftedChatProps.messages[0].image).toContain("/api/static/images/envless.png");
    });
  });

  it("handles invalid and unknown backend response shapes", async () => {
    mockedGetNewChatGroup.mockResolvedValue({ group_id: 3 } as any);
    mockedSendMessage.mockResolvedValueOnce(undefined as any);

    render(React.createElement(ChatPage));
    fireEvent.press(screen.getByTestId("gifted-send-trimmed"));

    await waitFor(() => {
      expect(alertMock).toHaveBeenCalledWith(
          "Error",
          "Received invalid response from server. Please try again.",
      );
    });

    mockedSendMessage.mockResolvedValueOnce({ prompt_type: "weird" } as any);
    fireEvent.press(screen.getByTestId("gifted-send-trimmed"));

    await waitFor(() => {
      expect(alertMock).toHaveBeenCalledWith(
          "Unknown response type",
          "Received unknown prompt type from server",
      );
      expect(warnMock).toHaveBeenCalled();
    });
  });

  it("handles send and group creation errors with fallback messages", async () => {
    mockedGetNewChatGroup.mockResolvedValue({ group_id: 9 } as any);
    mockedSendMessage.mockRejectedValueOnce({ status: 500, message: "send failed" });

    const firstRender = render(React.createElement(ChatPage));
    fireEvent.press(screen.getByTestId("gifted-send-trimmed"));

    await waitFor(() => {
      expect(alertMock).toHaveBeenCalledWith("Error Code: 500", "send failed");
    });

    firstRender.unmount();

    mockedGetNewChatGroup.mockRejectedValueOnce({});
    render(React.createElement(ChatPage));
    fireEvent.press(screen.getByTestId("gifted-send-trimmed"));

    await waitFor(() => {
      expect(alertMock).toHaveBeenCalledWith(
          "Error Code: Unknown",
          "Unknown error occurred while creating chat group.",
      );
    });
  });

  it("returns early for empty or missing outgoing messages", async () => {
    render(React.createElement(ChatPage));

    fireEvent.press(screen.getByTestId("gifted-send-empty"));
    fireEvent.press(screen.getByTestId("gifted-send-none"));
    fireEvent.press(screen.getByTestId("gifted-send-undefined"));
    fireEvent.press(screen.getByTestId("gifted-send-noarg"));

    await waitFor(() => {
      expect(mockedGetNewChatGroup).not.toHaveBeenCalled();
      expect(mockedSendMessage).not.toHaveBeenCalled();
    });
  });

  it("shows unknown send error details when message request rejects without fields", async () => {
    mockedGetNewChatGroup.mockResolvedValue({ group_id: 77 } as any);
    mockedSendMessage.mockRejectedValueOnce({});

    render(React.createElement(ChatPage));
    fireEvent.press(screen.getByTestId("gifted-send-trimmed"));

    await waitFor(() => {
      expect(alertMock).toHaveBeenCalledWith(
          "Error Code: Unknown",
          "Unknown error occurred while sending message.",
      );
    });
  });

  it("uses speech recognition result events and speaking flow when listening is active", async () => {
    mockedGetNewChatGroup.mockResolvedValue({ group_id: 11 } as any);
    mockedSendMessage.mockResolvedValue({ prompt_type: "question", answer: "ok" } as any);

    render(React.createElement(ChatPage));

    fireEvent.press(screen.getByTestId("feather-mic-off"));
    await waitFor(() => {
      expect(mockRequestPermissionsAsync).toHaveBeenCalled();
      expect(mockStart).toHaveBeenCalled();
    });

    await act(async () => {
      triggerSpeechResult("Hello, world!");
    });

    await waitFor(() => {
      expect(mockedSendMessage).toHaveBeenCalledWith("Hello, world!", 11);
    });
  });

  it("ignores empty speech transcript and stops listening", async () => {
    render(React.createElement(ChatPage));

    await act(async () => {
      triggerSpeechResult(undefined);
    });

    expect(mockedSendMessage).not.toHaveBeenCalled();
  });

  it("handles permission denied, manual stop path, and permission errors", async () => {
    mockRequestPermissionsAsync.mockResolvedValueOnce({ granted: false });
    render(React.createElement(ChatPage));

    fireEvent.press(screen.getByTestId("feather-mic-off"));
    await waitFor(() => {
      expect(warnMock).toHaveBeenCalledWith("Permissions not granted", { granted: false });
    });

    mockRequestPermissionsAsync.mockResolvedValueOnce({ granted: true });
    fireEvent.press(screen.getByTestId("feather-mic"));
    await waitFor(() => {
      expect(mockStop).toHaveBeenCalled();
    });

    mockRequestPermissionsAsync.mockRejectedValueOnce(new Error("perm error"));
    fireEvent.press(screen.getByTestId("feather-mic-off"));
    await waitFor(() => {
      expect(console.error).toHaveBeenCalled();
    });
  });

  it("stops recognition and speaks cleaned text when sending while listening", async () => {
    mockedGetNewChatGroup.mockResolvedValue({ group_id: 33 } as any);
    mockedSendMessage.mockResolvedValue({ prompt_type: "question", answer: "done" } as any);
    mockRequestPermissionsAsync.mockResolvedValueOnce({ granted: false });

    render(React.createElement(ChatPage));

    fireEvent.press(screen.getByTestId("feather-mic-off"));
    await waitFor(() => {
      expect(screen.getByTestId("feather-mic")).toBeTruthy();
    });

    fireEvent.press(screen.getByTestId("gifted-send-trimmed"));

    await waitFor(() => {
      expect(mockedSendMessage).toHaveBeenCalledWith("hello bot!", 33);
    });

    fireEvent.press(screen.getByTestId("gifted-send-trimmed"));

    await waitFor(() => {
      expect(mockedSendMessage).toHaveBeenCalledTimes(2);
      expect(mockStop).toHaveBeenCalled();
      expect(speakMock).toHaveBeenCalledWith("hello bot");
    });
  });

  it("renders dark mode colors and android spacer branch", async () => {
    mockedUseColorScheme.mockReturnValue("dark");
    Object.defineProperty(Platform, "OS", { configurable: true, value: "android" });
    mockedGetNewChatGroup.mockResolvedValue({ group_id: 21 } as any);
    mockedSendMessage.mockResolvedValue({ prompt_type: "question", answer: "x" } as any);

    const { UNSAFE_getAllByType } = render(React.createElement(ChatPage));
    fireEvent.press(screen.getByTestId("gifted-send-trimmed"));

    await waitFor(() => {
      expect(mockLatestGiftedChatProps.timeTextStyle.right.color).toBe("#381E72");
    });

    const viewNodes = UNSAFE_getAllByType(View);
    expect(viewNodes.length).toBeGreaterThan(0);
  });

  it("renders exported renderSend with configured styles", () => {
    render(
        React.createElement(renderSend as any, {
          text: "send",
          onSend: jest.fn(),
        }),
    );

    expect(screen.getByTestId("send")).toBeTruthy();
    expect(screen.getByText("send")).toBeTruthy();
  });
});









