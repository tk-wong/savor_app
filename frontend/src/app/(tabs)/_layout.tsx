import { Ionicons } from "@expo/vector-icons";
import {Tabs} from "expo-router";

export default function Layout() {
    return (
        <Tabs>
            <Tabs.Screen name="chatPage" options={{title:"Chat" , tabBarIcon: ({focused, color, size}) => {
                return <Ionicons name={focused ? "chatbubble-ellipses-sharp" : "chatbubble-ellipses-outline"} size={size} color={color} />                
            },}} />
            <Tabs.Screen name="allRecipePage" options={{title:"All Recipes" , tabBarIcon: ({focused, color, size}) => {
                return <Ionicons name={focused ? "receipt" : "receipt-outline"} size={size} color={color} />                
            },}} />
        </Tabs>
    )
}