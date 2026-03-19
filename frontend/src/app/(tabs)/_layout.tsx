import {Ionicons} from "@expo/vector-icons";
import {Tabs} from "expo-router";
import {useColorScheme} from "react-native";

export default function Layout() {
    const colorScheme = useColorScheme();
    const isDarkMode = colorScheme === "dark";
    return (
        <Tabs>
            <Tabs.Screen name="chatPage" options={{
                title: "Chat",
                tabBarIcon: ({focused, color, size}) => {
                    return <Ionicons name={focused ? "chatbubble-ellipses-sharp" : "chatbubble-ellipses-outline"}
                                     size={size} className={"!color-on-surface"}/>
                },
                sceneStyle: {backgroundColor: isDarkMode ? "#141218" : "#FEF7FF"},
                tabBarStyle: {backgroundColor: isDarkMode ? "#36343B" : "#E6E0E9"},
                tabBarLabelStyle: {color: isDarkMode ? "#E6E0E9" : "#1D1B20"},
            }}/>
            <Tabs.Screen name="allRecipePage" options={{
                title: "All Recipes", tabBarIcon: ({focused, color, size}) => {
                    return <Ionicons name={focused ? "receipt" : "receipt-outline"} size={size}
                                     className={"!color-on-surface"}/>
                },
            }}/>
        </Tabs>
    )
}