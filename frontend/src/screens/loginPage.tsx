import {SafeAreaView} from "react-native-safe-area-context";
import {useState} from "react";
import {Alert, StyleSheet, Text, TextInput, TouchableOpacity, useColorScheme} from "react-native";
import {login} from "../api";
import {router, Stack} from "expo-router";
import {cssInterop} from "nativewind";

export default function LoginPage() {
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")


    const loginHandler = () => {
        if (!email || !password) {
            Alert.alert("Error", "Please enter both email and password");
            return;
        }
        login(email, password).then((data) => {
            Alert.alert("Login successful");
            console.log(data);
            router.push("/chatPage");
        }).catch((error) => {
            Alert.alert("Login failed", `Error: ${error}`);
        });
    }

    const colorScheme = useColorScheme();
    const isDarkMode = colorScheme === "dark";
    return (
        <>
            <Stack.Screen
                options={{
                    headerShown: true,
                    title: "Welcome to Savor!",
                    headerTitleAlign: "center",
                    contentStyle: {
                        backgroundColor: isDarkMode ? "#141218" : "#FEF7FF",
                    },
                    headerStyle: {
                        backgroundColor: isDarkMode ? "#141218": "#FEF7FF",
                    },
                    headerTitleStyle: {
                        fontFamily: "inter-bold",
                        fontSize: 20,
                        color: isDarkMode ? "#E6E0E9" : "#1D1B20",
                    },
                    // contentStyle : {backgroundColor: "#FEF7FF"},

                }}

            />
            <SafeAreaView className={"flex gap-4 mx-auto w-full px-4 bg-surface"}
            >

                <Text className={"global-text text-on-surface"}>Email:</Text>
                <TextInput className={"global-text-input border-on-surface-variant"} placeholder={"User name"} onChangeText={setEmail}
                           id={"username_input"} />
                <Text className={"global-text text-on-surface"}>Password:</Text>
                <TextInput className={"global-text-input border-on-surface-variant"} secureTextEntry={true} placeholder={"Password"}
                           onChangeText={setPassword} id={"password_input"}/>
                <TouchableOpacity onPress={
                    loginHandler
                } className={"global-button  !bg-primary"}>
                    <Text className={"global-text !text-on-primary"}>Submit</Text>
                </TouchableOpacity>
                <TouchableOpacity onPress={() => {
                    // const message = "Create account"
                    router.navigate("/createUserPage")
                }} className={"global-button !border-primary !bg-transparent"}>
                    <Text className={"global-text !text-on-surface"}>Create account</Text>
                </TouchableOpacity>
                <TouchableOpacity onPress={() => {
                    // for debugging
                    router.push("/functionTestingPage")
                }} className={"global-button"}>
                    <Text className={"global-text"}>Function testing page</Text>
                </TouchableOpacity>

            </SafeAreaView>
        </>
    );
}

