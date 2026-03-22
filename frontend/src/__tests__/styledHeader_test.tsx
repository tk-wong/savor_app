import React from "react";
import { render } from "@testing-library/react-native";
import * as ReactNative from "react-native";
import { StyledHeader } from "../components/styledHeader";

let mockStackScreen: jest.Mock;

jest.mock("expo-router", () => {
  mockStackScreen = jest.fn(({ options }: { options: any }) => {
    // Eagerly call function options if provided
    if (typeof options === "function") {
      options({ route: { name: "test" } });
    }
    return null;
  });
  return {
    Stack: {
      Screen: mockStackScreen,
    },
  };
});

describe("StyledHeader component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders with object options and merges styles in dark mode", () => {
    jest.spyOn(ReactNative, "useColorScheme").mockReturnValue("dark");


    render(
      <StyledHeader
        title="Test Page"
        options={{
          // @ts-ignore
          headerStyle: { borderBottomWidth: 2 },
          headerTitleStyle: { fontSize: 24 },
          contentStyle: { paddingHorizontal: 16 },
        }}
      />,
    );

    expect(mockStackScreen).toHaveBeenCalled();
    const options = mockStackScreen.mock.calls[0][0].options;
    expect(options.title).toBe("Test Page");
    expect(options.headerStyle.backgroundColor).toBe("#141218");
    expect(options.headerStyle.borderBottomWidth).toBe(2);
    expect(options.headerTitleStyle.fontSize).toBe(24);
  });

  it("renders with function options and merges resolved styles", () => {
    jest.spyOn(ReactNative, "useColorScheme").mockReturnValue("light");

    const optionFactory = jest.fn(() => ({
      headerStyle: { borderBottomColor: "#999" },
      headerTitleStyle: { fontSize: 18 },
    }));

    render(<StyledHeader title="Dynamic" options={optionFactory as any} />);

    expect(mockStackScreen).toHaveBeenCalled();
    const optionsResolver = mockStackScreen.mock.calls[0][0].options;
    const resolved = optionsResolver({ route: { name: "dynamic" } });

    expect(resolved.title).toBe("Dynamic");
    expect(resolved.headerStyle.backgroundColor).toBe("#FEF7FF");
    expect(resolved.headerStyle.borderBottomColor).toBe("#999");
    expect(resolved.headerTitleStyle.fontSize).toBe(18);
  });

  it("renders with undefined function result and falls back to defaults", () => {
    jest.spyOn(ReactNative, "useColorScheme").mockReturnValue("light");

    const optionFactory = jest.fn(() => undefined);

    render(<StyledHeader title="Fallback" options={optionFactory as any} />);

    expect(mockStackScreen).toHaveBeenCalled();
    const optionsResolver = mockStackScreen.mock.calls[0][0].options;
    const resolved = optionsResolver({ route: { name: "fallback" } });

    expect(resolved.title).toBe("Fallback");
    expect(resolved.headerStyle.backgroundColor).toBe("#FEF7FF");
    expect(resolved.headerTitleStyle.color).toBe("#1D1B20");
    expect(resolved.contentStyle.backgroundColor).toBe("#FEF7FF");
  });

  it("renders with no options prop", () => {
    jest.spyOn(ReactNative, "useColorScheme").mockReturnValue("dark");

    render(<StyledHeader title="No Options" />);

    expect(mockStackScreen).toHaveBeenCalled();
    const options = mockStackScreen.mock.calls[0][0].options;
    expect(options.title).toBe("No Options");
    expect(options.headerStyle.backgroundColor).toBe("#141218");
    expect(options.headerTitleStyle.color).toBe("#E6E0E9");
  });

  it("covers mergeStyles null coalescing for function options that partially override styles", () => {
    jest.spyOn(ReactNative, "useColorScheme").mockReturnValue("light");

    const optionFactory = jest.fn(() => ({
      headerStyle: { borderBottomWidth: 1 },
      // headerTitleStyle intentionally undefined to test null coalescing
      // contentStyle intentionally undefined to test null coalescing
    }));

    render(<StyledHeader title="Partial Override" options={optionFactory as any} />);

    expect(mockStackScreen).toHaveBeenCalled();
    const optionsResolver = mockStackScreen.mock.calls[0][0].options;
    const resolved = optionsResolver({ route: { name: "partial" } });

    expect(resolved.title).toBe("Partial Override");
    // Should have base backgroundColor merged with partial override
    expect(resolved.headerStyle.backgroundColor).toBe("#FEF7FF");
    expect(resolved.headerStyle.borderBottomWidth).toBe(1);
    // These should use base values when override doesn't provide them
    expect(resolved.headerTitleStyle.color).toBe("#1D1B20");
    expect(resolved.contentStyle.backgroundColor).toBe("#FEF7FF");
  });

  it("covers mergeStyles for object options (non-function path)", () => {
    jest.spyOn(ReactNative, "useColorScheme").mockReturnValue("dark");


    render(
      <StyledHeader
        title="Object Path"
        options={{
          // @ts-ignore
          headerStyle: { elevation: 0 },
          // @ts-ignore
          headerTitleStyle: { letterSpacing: 0.5 },
          contentStyle: { flex: 1 },
        }}
      />,
    );

    expect(mockStackScreen).toHaveBeenCalled();
    const options = mockStackScreen.mock.calls[0][0].options;
    expect(options.title).toBe("Object Path");
    // Base should merge with overrides
    expect(options.headerStyle.backgroundColor).toBe("#141218");
    expect(options.headerStyle.elevation).toBe(0);
    expect(options.headerTitleStyle.color).toBe("#E6E0E9");
    expect(options.headerTitleStyle.letterSpacing).toBe(0.5);
    expect(options.contentStyle).toHaveProperty("flex", 1);
  });

  it("tests mergeStyles with both sides having values", () => {
    jest.spyOn(ReactNative, "useColorScheme").mockReturnValue("light");

    const optionFactory = jest.fn(() => ({
      headerStyle: { backgroundColor: "#fff" },
      headerTitleStyle: { color: "#000" },
      contentStyle: { paddingTop: 10 },
    }));

    render(<StyledHeader title="Both Sides" options={optionFactory as any} />);

    const optionsResolver = mockStackScreen.mock.calls[0][0].options;
    const resolved = optionsResolver({ route: { name: "both" } });

    // Override should take precedence in spread
    expect(resolved.headerStyle.backgroundColor).toBe("#fff");
    expect(resolved.headerTitleStyle.color).toBe("#000");
    expect(resolved.contentStyle.paddingTop).toBe(10);
  });

  it("covers function options returning empty objects to test mergeStyles with null values", () => {
    jest.spyOn(ReactNative, "useColorScheme").mockReturnValue("light");

    const optionFactory = jest.fn(() => ({
      headerStyle: {},
      headerTitleStyle: {},
      contentStyle: {},
    }));

    render(<StyledHeader title="Empty Override" options={optionFactory as any} />);

    const optionsResolver = mockStackScreen.mock.calls[0][0].options;
    const resolved = optionsResolver({ route: { name: "empty" } });

    expect(resolved.title).toBe("Empty Override");
    // Should have base values when overrides are empty
    expect(resolved.headerStyle.backgroundColor).toBe("#FEF7FF");
    expect(resolved.headerTitleStyle.color).toBe("#1D1B20");
    expect(resolved.contentStyle.backgroundColor).toBe("#FEF7FF");
  });
});

