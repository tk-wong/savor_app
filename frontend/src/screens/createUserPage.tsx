import { ScrollView, Text, TextInput, TouchableOpacity, Alert, StyleSheet } from "react-native";
import { Stack, useRouter } from "expo-router";
import { createUser } from "../api";
import { useState } from "react";
import { isAxiosError } from "axios";

const style = StyleSheet.create(
    {
        button: {
            alignItems: 'center',
            backgroundColor: '#DDDDDD',
            padding: 20,
        },
    }
)

export default function CreateUserPage() {
    const router = useRouter();
    const [email, setEmail] = useState("");
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const createUserHandler = async () => {
        if (!email || !username || !password) {
            Alert.alert("Error", "Please fill in all fields");
            return;
        }
        try {
            const response = await createUser(email, username, password);
            Alert.alert("User created", "User created successfully! Please log in.");
            router.navigate("/loginPage");
        } catch (error) {
            // Alert.alert("Error", "Failed to create user.");
            if (isAxiosError(error)) {
                console.error("Axios error details:", {
                    message: error.message,
                    response: error.response
                        ? {
                            status: error.response.status,
                            data: error.response.data,
                        }
                        : null,
                });
                if (error.status === 400) {
                    Alert.alert("Error", "Invalid input. Please check your email, username, and password.");
                }else if (error.status === 409) {
                    Alert.alert("Error", "User already exists. Please use a different email or username.");
                } else {
                    Alert.alert("Error", "Failed to create user. Please try again.");
                }
            } else {
                console.error("Unexpected error:", error);
                Alert.alert("Error", "An unexpected error occurred. Please try again.");
            }
        }
    };
    return (
        <>
            <Stack.Screen
                options={{
                    headerShown: true,
                    title: "Create User",
                }}
            />
            <ScrollView>
                <Text>{"Enter your name"}</Text>
                <TextInput style={{ borderWidth: 1 }} id={"username"} onChangeText={setUsername} />
                <Text>{"Enter your email"}</Text>
                <TextInput style={{ borderWidth: 1 }} id={"email"} onChangeText={setEmail} />
                <Text>{"Enter your password"}</Text>
                <TextInput style={{ borderWidth: 1 }} secureTextEntry={true} id={"password"} onChangeText={setPassword} />
                <TouchableOpacity onPress={createUserHandler
                } style={style.button}>
                    <Text>Submit</Text>
                </TouchableOpacity>
                <TouchableOpacity onPress={() => {
                    // for debugging
                    router.navigate("/loginPage")
                }

                } style={style.button}>

                    <Text>Back to Login page</Text>
                </TouchableOpacity>
            </ScrollView>
        </>
    )

}

