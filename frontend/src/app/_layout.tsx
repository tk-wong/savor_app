import {Stack} from "expo-router";
import {Inter_400Regular, Inter_400Regular_Italic, Inter_700Bold, Inter_700Bold_Italic} from "@expo-google-fonts/inter";
import {useFonts} from "expo-font";
import {useColorScheme} from "react-native";

export default function RootLayout() {
    const [fontLoaded, fontError] = useFonts({
        "inter": Inter_400Regular,
        "inter-italic": Inter_400Regular_Italic,
        "inter-bold": Inter_700Bold,
        "inter-bold-italic": Inter_700Bold_Italic,
    });
    if (fontError) {
        console.error("Cannot load font", fontError);
    }

    if (!fontLoaded && !fontError) {
        console.log("loading font...");
        return null;
    }
    // const colorScheme = useColorScheme();
    //  const isDarkMode = colorScheme === "dark";
    return (
        <Stack >
            <Stack.Screen name="loginPage" options={{headerShown: false}} />
            <Stack.Screen name="(tabs)" options={{headerShown: false}}/>
        </Stack>
    );
}
