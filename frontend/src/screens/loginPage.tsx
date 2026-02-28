
import { SafeAreaView } from "react-native-safe-area-context";
import { useState } from "react";
import { Alert, StyleSheet, Text, TextInput, TouchableOpacity, View } from "react-native";
import { login, testUser } from "../api";
import { router } from "expo-router";

export default function LoginPage() {
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")


    
    const loginHandler = () => {
        if (!email || !password) {
            Alert.alert("Error", "Please enter both email and password");
            return;
        }
        login(email, password).then((data) => {
            Alert.alert("Login successful", `Token: ${data.token}`);
            console.log(data);
        }).catch((error) => {
            Alert.alert("Login failed", `Error: ${error}`);
        });
    }
    return (
        <SafeAreaView
            // style={{
            //     flex: 1,
            //     justifyContent: "center",
            //     alignItems: "center",
            // }}
        >
            <Text>Welcome</Text>
            <Text>Email:</Text>
            <TextInput style={{ borderWidth: 1 }} placeholder={"User name"} onChangeText={setEmail}
                id={"username_input"} />
            <Text>Password</Text>
            <TextInput style={{ borderWidth: 1 }} secureTextEntry={true} placeholder={"Password"}
                onChangeText={setPassword} id={"password_input"} />
            <TouchableOpacity onPress={
                loginHandler
            }
                style={style.button}>
                <Text>Submit</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => {
                // const message = "Create account"
                router.navigate("/createUserPage")
            }} style={style.button}>
                <Text>Create account</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => {
                // for debugging
                router.push("/functionTestingPage")
            }} style={style.button}>
                <Text>Function testing page</Text>
            </TouchableOpacity>

        </SafeAreaView >
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
