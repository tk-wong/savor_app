import React from "react";
import { Image } from "react-native";
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react-native";
import RecipePage from "../screens/recipePage";
import { getRecipeById } from "../api/recipe";
import { useTextToSpeech } from "../hooks/useTextToSpeech";
import { useSpeechToText } from "../hooks/useSpeechToText";

jest.mock("../api/recipe", () => ({
  getRecipeById: jest.fn(),
}));

jest.mock("../hooks/useTextToSpeech", () => ({
  useTextToSpeech: jest.fn(),
}));

jest.mock("../hooks/useSpeechToText", () => ({
  useSpeechToText: jest.fn(),
}));

const mockRouterBack = jest.fn();
const mockUseLocalSearchParams = jest.fn();

jest.mock("expo-router", () => ({
  router: {
    back: (...args: unknown[]) => mockRouterBack(...args),
  },
  useLocalSearchParams: () => mockUseLocalSearchParams(),
  useFocusEffect: (effect: () => void) => {
    const ReactLocal = require("react");
    ReactLocal.useEffect(() => {
      effect();
    }, [effect]);
  },
}));

const mockSpeechCallbacks: Record<string, ((event?: any) => void) | undefined> = {};
const mockSpeechRecognitionStop = jest.fn();

jest.mock("expo-speech-recognition", () => ({
  ExpoSpeechRecognitionModule: {
    stop: (...args: unknown[]) => mockSpeechRecognitionStop(...args),
  },
  useSpeechRecognitionEvent: (eventName: string, callback: (event?: any) => void) => {
    mockSpeechCallbacks[eventName] = callback;
  },
}));

jest.mock("../components/styledHeader", () => ({
  StyledHeader: ({ title }: { title: string }) => {
    const ReactLocal = require("react");
    const { Text } = require("react-native");
    return ReactLocal.createElement(Text, { testID: "styled-header" }, title);
  },
}));

jest.mock("@expo/vector-icons/AntDesign", () => ({
  __esModule: true,
  default: ({ onPress, name }: { onPress?: () => void; name: string }) => {
    const ReactLocal = require("react");
    const { Pressable, Text } = require("react-native");
    return ReactLocal.createElement(
        Pressable,
        { testID: `ant-${name}`, onPress },
        ReactLocal.createElement(Text, null, name),
    );
  },
}));

jest.mock("react-native-safe-area-context", () => ({
  SafeAreaView: ({ children }: { children: React.ReactNode }) => {
    const ReactLocal = require("react");
    const { View } = require("react-native");
    return ReactLocal.createElement(View, { testID: "safe-area" }, children);
  },
}));

describe("RecipePage", () => {
  const mockedGetRecipeById = getRecipeById as jest.MockedFunction<typeof getRecipeById>;
  const mockedUseTextToSpeech = useTextToSpeech as jest.Mock;
  const mockedUseSpeechToText = useSpeechToText as jest.Mock;
  const mockSpeak = jest.fn();
  const mockStopSpeaking = jest.fn();
  const mockStartListening = jest.fn();
  const mockStopListening = jest.fn();
  const logSpy = jest.spyOn(console, "log").mockImplementation(() => {});
  const warnSpy = jest.spyOn(console, "warn").mockImplementation(() => {});
  const errorSpy = jest.spyOn(console, "error").mockImplementation(() => {});
  const originalBackendUrl = process.env.EXPO_PUBLIC_BACKEND_URL;

  const recipePayload = {
    recipe: {
      id: 101,
      title: "Test Recipe",
      description: "Delicious food",
      image_url: "https://cdn.test/recipe.png",
      ingredients: [
        { name: "Eggs", quantity: "2" },
        { name: "Flour", quantity: "1 cup" },
      ],
      directions: ["Step one", "Step two"],
      tips: ["Be patient"],
    },
  } as any;

  const triggerSpeechResult = async (transcript: string) => {
    await act(async () => {
      const cb = mockSpeechCallbacks.result;
      cb?.({ results: [{ transcript }] });
    });
  };

  const triggerSpeechEnd = async () => {
    await act(async () => {
      const cb = mockSpeechCallbacks.end;
      cb?.();
    });
  };

  beforeEach(() => {
    jest.clearAllMocks();
    Object.keys(mockSpeechCallbacks).forEach((key) => {
      delete mockSpeechCallbacks[key];
    });
    mockUseLocalSearchParams.mockReturnValue({ id: "101" });
    mockedGetRecipeById.mockResolvedValue(recipePayload);
    mockSpeak.mockResolvedValue(undefined);
    mockStopSpeaking.mockResolvedValue(undefined);
    mockedUseTextToSpeech.mockReturnValue({
      speak: mockSpeak,
      stopSpeaking: mockStopSpeaking,
    });
    mockedUseSpeechToText.mockReturnValue({
      startListening: mockStartListening,
      stopListening: mockStopListening,
    });
    process.env.EXPO_PUBLIC_BACKEND_URL = "https://api.test/api";
    jest.useRealTimers();
  });

  afterEach(() => {
    process.env.EXPO_PUBLIC_BACKEND_URL = originalBackendUrl;
  });

  it("fetches and renders recipe details with remote image", async () => {
    const { UNSAFE_getAllByType } = render(React.createElement(RecipePage));

    await waitFor(() => {
      expect(mockedGetRecipeById).toHaveBeenCalledWith(101);
      expect(screen.getByText("Test Recipe")).toBeTruthy();
      expect(screen.getByText("1. Step one")).toBeTruthy();
      expect(screen.getByText("2. Step two")).toBeTruthy();
    });

    const images = UNSAFE_getAllByType(Image);
    expect(images[0].props.source).toEqual({ uri: "https://cdn.test/recipe.png" });
  });

  it("falls back to default recipe data and placeholder image when fetch fails", async () => {
    mockedGetRecipeById.mockRejectedValueOnce(new Error("network"));
    const { UNSAFE_getAllByType } = render(React.createElement(RecipePage));

    await waitFor(() => {
      expect(screen.getByText("Recipe not found")).toBeTruthy();
    });

    const images = UNSAFE_getAllByType(Image);
    expect(images[0].props.source).toEqual({
      uri: "https://blocks.astratic.com/img/general-img-square.png",
    });
  });

  it("normalizes relative image paths and ingredient fallback rendering", async () => {
    delete process.env.EXPO_PUBLIC_BACKEND_URL;
    mockedGetRecipeById.mockResolvedValueOnce({
      recipe: {
        id: 202,
        title: "Relative Path Recipe",
        description: "Desc",
        image_url: "static\\images\\r.png",
        ingredients: [
          "Raw ingredient",
          {},
          { name: "Flour", quantity: "1 cup" },
          { name: "Salt", quantity: "" },
          { name: "", quantity: "2 tbsp" },
          { name: "", quantity: "" },
        ],
        directions: ["Step one"],
        tips: ["Tip"],
      },
    } as any);

    const { UNSAFE_getAllByType } = render(React.createElement(RecipePage));

    await waitFor(() => {
      expect(screen.getByText("Raw ingredient")).toBeTruthy();
      expect(screen.getByText("1 cup Flour")).toBeTruthy();
      expect(screen.getByText("Salt")).toBeTruthy();
      expect(screen.getByText("2 tbsp")).toBeTruthy();
      expect(screen.getAllByText("N/A").length).toBeGreaterThan(0);
    });

    const images = UNSAFE_getAllByType(Image);
    expect(images[0].props.source.uri).toContain("/static/images/r.png");
  });

  it("normalizes duplicated /api prefix in recipe image paths", async () => {
    process.env.EXPO_PUBLIC_BACKEND_URL = "https://api.test/api";
    mockedGetRecipeById.mockResolvedValueOnce({
      recipe: {
        id: 203,
        title: "Api Prefix Recipe",
        description: "Desc",
        image_url: "/api/static/images/dedupe.png",
        ingredients: [{ name: "Egg", quantity: "1" }],
        directions: ["Step one"],
        tips: ["Tip"],
      },
    } as any);

    const { UNSAFE_getAllByType } = render(React.createElement(RecipePage));

    await waitFor(() => {
      expect(screen.getByText("Api Prefix Recipe")).toBeTruthy();
    });

    const images = UNSAFE_getAllByType(Image);
    expect(images[0].props.source.uri).toBe("https://api.test/api/static/images/dedupe.png");
  });

  it("normalizes malformed recipe fields and ignores empty speech result payloads", async () => {
    mockedGetRecipeById.mockResolvedValueOnce({
      recipe: {
        id: undefined,
        title: undefined,
        description: undefined,
        image_url: undefined,
        ingredients: {},
        directions: {},
        tips: {},
      },
    } as any);

    const { UNSAFE_getAllByType } = render(React.createElement(RecipePage));

    await waitFor(() => {
      expect(screen.getByText("Recipe not found")).toBeTruthy();
    });

    fireEvent.press(screen.getByText("start voice interaction"));
    fireEvent.press(screen.getByTestId("ant-plus"));

    await act(async () => {
      const cb = mockSpeechCallbacks.result;
      cb?.({ results: [{}] });
    });

    expect(mockSpeak).not.toHaveBeenCalled();
    expect(mockStartListening).toHaveBeenCalled();

    const images = UNSAFE_getAllByType(Image);
    expect(images[0].props.source.uri).toBe("https://blocks.astratic.com/img/general-img-square.png");
  });

  it("starts and stops voice interaction from the main toggle", async () => {
    render(React.createElement(RecipePage));

    await waitFor(() => {
      expect(screen.getByText("start voice interaction")).toBeTruthy();
    });

    fireEvent.press(screen.getByText("start voice interaction"));

    await waitFor(() => {
      expect(mockSpeak).toHaveBeenCalledWith("Step one");
      expect(mockStartListening).toHaveBeenCalled();
    });

    fireEvent.press(screen.getByText("stop voice interaction "));

    expect(mockSpeechRecognitionStop).toHaveBeenCalled();
  });

  it("handles speech result commands for next, previous/back, repeat, and reset", async () => {
    jest.useFakeTimers();
    render(React.createElement(RecipePage));
    fireEvent.press(await screen.findByText("start voice interaction"));

    await waitFor(() => {
      expect(mockSpeak).toHaveBeenCalledWith("Step one");
    });

    await act(async () => {
      jest.advanceTimersByTime(160);
    });

    await triggerSpeechResult("next");
    await waitFor(() => {
      expect(mockSpeak).toHaveBeenCalledWith("Step two");
    });

    await act(async () => {
      jest.advanceTimersByTime(160);
    });

    const beforeEndNext = mockSpeak.mock.calls.length;
    await triggerSpeechResult("next");
    expect(mockSpeak.mock.calls.length).toBe(beforeEndNext);

    await triggerSpeechResult("previous step");
    await waitFor(() => {
      expect(mockSpeak).toHaveBeenCalledWith("Step one");
    });

    await triggerSpeechResult("repeat");
    await waitFor(() => {
      expect(mockStopSpeaking).toHaveBeenCalled();
    });

    await triggerSpeechResult("reset");
    await waitFor(() => {
      expect(mockStopSpeaking).toHaveBeenCalled();
    });

    await act(async () => {
      jest.advanceTimersByTime(160);
    });

    await triggerSpeechResult("back");
    await triggerSpeechResult("unrelated words");
  });

  it("supports navigation controls and back button", async () => {
    render(React.createElement(RecipePage));

    await waitFor(() => {
      expect(screen.getByText("Repeat")).toBeTruthy();
      expect(screen.getByText("Reset")).toBeTruthy();
      expect(screen.getByText("Stop")).toBeTruthy();
    });

    fireEvent.press(screen.getByText("Repeat"));
    fireEvent.press(screen.getByText("Reset"));
    fireEvent.press(screen.getByText("Stop"));
    fireEvent.press(screen.getByTestId("ant-plus"));
    fireEvent.press(screen.getByTestId("ant-minus"));
    fireEvent.press(screen.getByText("Back"));

    expect(mockRouterBack).toHaveBeenCalled();
    expect(mockStopSpeaking).toHaveBeenCalled();
  });

  it("handles button-based next navigation and stops at the last step", async () => {
    jest.useFakeTimers();
    render(React.createElement(RecipePage));

    await waitFor(() => {
      expect(screen.getByText("1. Step one")).toBeTruthy();
    });

    fireEvent.press(screen.getByTestId("ant-plus"));
    await act(async () => {
      jest.advanceTimersByTime(160);
    });

    fireEvent.press(screen.getByTestId("ant-plus"));
    await act(async () => {
      jest.advanceTimersByTime(160);
    });

    fireEvent.press(screen.getByTestId("ant-minus"));
    await act(async () => {
      jest.advanceTimersByTime(160);
    });

    fireEvent.press(screen.getByTestId("ant-plus"));
    await act(async () => {
      jest.advanceTimersByTime(160);
    });

    const beforeBoundary = mockSpeak.mock.calls.length;
    fireEvent.press(screen.getByTestId("ant-plus"));
    await act(async () => {
      jest.advanceTimersByTime(160);
    });

    expect(mockSpeak.mock.calls.length).toBe(beforeBoundary);
  });

  it("restarts listening on speech end without replaying step 0", async () => {
    jest.useFakeTimers();
    render(React.createElement(RecipePage));

    fireEvent.press(await screen.findByText("start voice interaction"));

    await waitFor(() => {
      expect(mockSpeak).toHaveBeenCalledWith("Step one");
    });

    await act(async () => {
      jest.advanceTimersByTime(160);
    });

    const beforeEndSpeakCalls = mockSpeak.mock.calls.length;
    const beforeEndStartListeningCalls = mockStartListening.mock.calls.length;
    await triggerSpeechEnd();

    act(() => {
      jest.advanceTimersByTime(110);
    });

    await waitFor(() => {
      expect(mockStartListening.mock.calls.length).toBeGreaterThan(beforeEndStartListeningCalls);
    });
    expect(mockSpeak.mock.calls.length).toBe(beforeEndSpeakCalls);
  });

  it("logs speech errors when speak fails and when auto-restart listening fails", async () => {
    jest.useFakeTimers();
    const speakError = new Error("tts-fail");
    mockSpeak.mockRejectedValueOnce(speakError);
    mockStartListening.mockImplementationOnce(() => {
      throw new Error("stt-restart-fail");
    });

    render(React.createElement(RecipePage));
    fireEvent.press(await screen.findByText("start voice interaction"));

    await act(async () => {
      jest.advanceTimersByTime(160);
    });

    expect(errorSpy).toHaveBeenCalledWith("[Voice] Error during speakStep:", speakError);
  });

  it("handles non-button voice commands while listening and catches stopListening errors", async () => {
    jest.useFakeTimers();
    mockStopListening.mockImplementation(() => {
      throw new Error("stop-fail");
    });

    render(React.createElement(RecipePage));
    fireEvent.press(await screen.findByText("start voice interaction"));

    await act(async () => {
      jest.advanceTimersByTime(160);
    });

    await waitFor(() => {
      expect(screen.getByText("stop voice interaction ")).toBeTruthy();
    });

    await triggerSpeechResult("next step");
    await act(async () => {
      jest.advanceTimersByTime(160);
    });

    await triggerSpeechResult("previous");
    await act(async () => {
      jest.advanceTimersByTime(160);
    });

    await triggerSpeechResult("repeat");
    await act(async () => {
      jest.advanceTimersByTime(160);
    });

    await triggerSpeechResult("reset");
    await act(async () => {
      jest.advanceTimersByTime(160);
    });

    expect(warnSpy).toHaveBeenCalled();
  });

  it("handles speech/listening errors and lock guard branches without crashing", async () => {
    jest.useFakeTimers();

    let resolveSpeak: (() => void) | null = null;
    mockSpeak
        .mockImplementationOnce(
            () =>
                new Promise<void>((resolve) => {
                  resolveSpeak = resolve;
                }),
        )
        .mockResolvedValue(undefined);

    mockStopListening.mockImplementation(() => {
      throw new Error("stop listening failed");
    });
    mockStartListening.mockImplementationOnce(() => {
      throw new Error("start listening failed");
    });

    render(React.createElement(RecipePage));
    fireEvent.press(await screen.findByText("start voice interaction"));

    await waitFor(() => {
      expect(mockSpeak).toHaveBeenCalledTimes(1);
    });

    // While first TTS call is locked/pending, this should hit the ttsLockRef guard.
    await triggerSpeechResult("next");
    expect(mockSpeak).toHaveBeenCalledTimes(1);

    act(() => {
      resolveSpeak?.();
    });

    await act(async () => {
      jest.advanceTimersByTime(160);
    });

    mockSpeak.mockRejectedValueOnce(new Error("tts failure"));
    fireEvent.press(screen.getByTestId("ant-plus"));

    await waitFor(() => {
      expect(warnSpy).toHaveBeenCalled();
    });

    // Exercise end handler no-restart branch when not listening.
    const before = mockSpeak.mock.calls.length;
    await triggerSpeechEnd();
    act(() => {
      jest.advanceTimersByTime(120);
    });
    expect(mockSpeak.mock.calls.length).toBe(before);
  });

  afterAll(() => {
    logSpy.mockRestore();
    warnSpy.mockRestore();
    // Keep console.error mocked for jest.setup.js teardown compatibility.
  });
});








