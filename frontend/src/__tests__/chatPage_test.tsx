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
    mockRequestPermissionsAsync.mockResolvedValue({ granted: true });
    Object.defineProperty(Platform, "OS", { configurable: true, value: "ios" });
  });

  afterEach(() => {
    Object.defineProperty(Platform, "OS", { configurable: true, value: originalPlatformOS });
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
        name: "Tomato Soup",
        description: "A cozy soup",
        ingredients: ["Tomato", "Salt"],
        instructions: ["Boil", "Serve"],
        tips: ["Use ripe tomatoes"],
        image_url: null,
      },
    } as any);

    const firstRender = render(React.createElement(ChatPage));
    fireEvent.press(screen.getByTestId("gifted-send-trimmed"));

    await waitFor(() => {
      expect(mockedSendMessage).toHaveBeenCalledWith("hello bot!", 55);
    });
    await waitFor(() => {
      expect(mockLatestGiftedChatProps.messages[0].image).toBeUndefined();
      expect(mockLatestGiftedChatProps.messages[0].text).toContain("Here's a recipe for you");
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









