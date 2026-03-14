import {useColorScheme} from "react-native";
import {Stack} from "expo-router";

export function Styleeheader({title}: { title: string }) {
    const colorScheme = useColorScheme();
    const isDarkMode = colorScheme === "dark";
    return <Stack.Screen
        options={{
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
            // contentStyle : {backgroundColor: "#FEF7FF"},

        }}

    />;
}