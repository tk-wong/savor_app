import {SafeAreaView} from "react-native-safe-area-context";
import {useState} from "react";
import {Alert, Text, TextInput, TouchableOpacity, useColorScheme, View} from "react-native";
import {login} from "../api";
import {router, Stack} from "expo-router";

function LoginHeader() {
    const colorScheme = useColorScheme();
    const isDarkMode = colorScheme === "dark";
    return <Stack.Screen
        options={{
            headerShown: true,
            title: "Welcome to Savor!",
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

function LoginView() {
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
    return <SafeAreaView className={"flex gap-4 mx-auto w-full px-4 bg-surface"}
    >

        <Text className={"global-text text-on-surface"}>Email:</Text>
        <TextInput className={"global-text-input border-on-surface-variant text-on-surface-variant"}
                   placeholder={"User name"}
                   onChangeText={setEmail}
                   id={"username_input"} value={email}/>
        <Text className={"global-text text-on-surface"}>Password:</Text>
        <TextInput className={"global-text-input border-on-surface-variant text-on-surface-variant"}
                   secureTextEntry={true}
                   placeholder={"Password"}
                   onChangeText={setPassword} id={"password_input"}
                   value={password}/>
        <View className={"flex-row gap-4 items-center align-middle"}>
            <TouchableOpacity onPress={() => {
                setEmail("");
                setPassword("")
            }} className={"global-button  !bg-primary-container flex-1"}>
                <Text className={"global-text !text-on-primary-container"}>Reset</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={
                loginHandler
            } className={"global-button  !bg-primary flex-1"}>
                <Text className={"global-text !text-on-primary"}>Submit</Text>
            </TouchableOpacity>

        </View>
        <TouchableOpacity onPress={() => {
            // const message = "Create account"
            router.navigate("/createUserPage")
        }} className={"global-button bg-secondary"}>
            <Text className={"global-text !text-on-secondary"}>Create account</Text>
        </TouchableOpacity>
        <TouchableOpacity onPress={() => {
            // for debugging
            router.push("/functionTestingPage")
        }} className={"global-button bg-gray-400"}>
            <Text className={"global-text"}>Function testing page</Text>
        </TouchableOpacity>

    </SafeAreaView>;
}

export default function LoginPage() {
    return (
        <>
            <LoginHeader/>
            <LoginView/>
        </>
    );
}

