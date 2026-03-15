import {useColorScheme} from "react-native";
import {Stack} from "expo-router";
import type {ComponentProps} from "react";

type StackScreenOptions = ComponentProps<typeof Stack.Screen>["options"];

export function StyledHeader({title, options}: { title: string; options?: StackScreenOptions }) {
    const colorScheme = useColorScheme();
    const isDarkMode = colorScheme === "dark";

    const baseOptions: NonNullable<StackScreenOptions> = {
        headerShown: true,
        title: title,
        headerTitleAlign: "center",
        contentStyle: {
            backgroundColor: isDarkMode ? "#141218" : "#FEF7FF",
        },
        headerStyle: {
            backgroundColor: isDarkMode ? "#141218" : "#FEF7FF",
        },
        headerTitleStyle: {
            fontFamily: "inter-bold",
            fontSize: 20,
            color: isDarkMode ? "#E6E0E9" : "#1D1B20",
        },
    };

    // Helper to merge nested style-like objects safely
    const mergeStyles = (a: any, b: any) => ({ ...(a ?? {}), ...(b ?? {}) });

    // If options is a function, return a function that resolves it and merges with baseOptions
    if (typeof options === "function") {
        return <Stack.Screen
            options={(props: any) => {
                const resolved = (options as Function)(props) as any;
                return {
                    ...(baseOptions as any),
                    ...(resolved ?? {}),
                    headerStyle: mergeStyles((baseOptions as any).headerStyle, resolved?.headerStyle),
                    headerTitleStyle: mergeStyles((baseOptions as any).headerTitleStyle, resolved?.headerTitleStyle),
                    contentStyle: mergeStyles((baseOptions as any).contentStyle, resolved?.contentStyle),
                } as any;
            }}
        />;
    }

    // Otherwise options is an object (or undefined) and we can shallow-merge directly
    const optObj = (options as any) ?? {};

    const mergedOptions: StackScreenOptions = {
        ...(baseOptions as any),
        ...optObj,
        headerStyle: mergeStyles((baseOptions as any).headerStyle, optObj.headerStyle),
        headerTitleStyle: mergeStyles((baseOptions as any).headerTitleStyle, optObj.headerTitleStyle),
        contentStyle: mergeStyles((baseOptions as any).contentStyle, optObj.contentStyle),
    } as any;

    return <Stack.Screen
        options={mergedOptions}
    />;
}