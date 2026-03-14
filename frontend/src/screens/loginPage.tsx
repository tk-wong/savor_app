import {SafeAreaView} from "react-native-safe-area-context";
import {useState} from "react";
import {Alert, StyleSheet, Text, TextInput, TouchableOpacity} from "react-native";
import {login} from "../api";
import {router, Stack} from "expo-router";

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
    return (
        <>
            <Stack.Screen
                options={{
                    headerShown: true,
                    title: "Welcome",
                    headerTitleAlign: "center",
                }}

            />
            <SafeAreaView className={"flex gap-4 mx-auto w-full px-4"}
            >

                <Text>Email:</Text>
                <TextInput className={"global-text-input"} placeholder={"User name"} onChangeText={setEmail}
                           id={"username_input"}/>
                <Text>Password</Text>
                <TextInput className={"global-text-input"} secureTextEntry={true} placeholder={"Password"}
                           onChangeText={setPassword} id={"password_input"}/>
                <TouchableOpacity onPress={
                    loginHandler
                } className={"global-button"}>
                    <Text>Submit</Text>
                </TouchableOpacity>
                <TouchableOpacity onPress={() => {
                    // const message = "Create account"
                    router.navigate("/createUserPage")
                }} className={"global-button"}>
                    <Text>Create account</Text>
                </TouchableOpacity>
                <TouchableOpacity onPress={() => {
                    // for debugging
                    router.push("/functionTestingPage")
                }} className={"global-button"}>
                    <Text>Function testing page</Text>
                </TouchableOpacity>

            </SafeAreaView>
        </>
    );
}
const style = StyleSheet.create(
    {
        button: {
            alignItems: 'center',
            backgroundColor: '#DDDDDD',
            padding: 20,
        },
    }
)
