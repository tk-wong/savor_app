import {Alert, StyleSheet, Text, TextInput, TouchableOpacity, View} from "react-native";
import {useRouter} from "expo-router";
import {createUser} from "../api";
import {useState} from "react";
import {isAxiosError} from "axios";
import {StyledHeader} from "@/src/components/styledHeader";
import {SafeAreaView} from "react-native-safe-area-context";


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
                } else if (error.status === 409) {
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
            <StyledHeader title={"Creat User"}/>
            <SafeAreaView className={"flex-1 bg-surface p-safe gap-4 px-safe-or-4"}>
                <View className={" justify-between gap-2"}>
                    <Text className={"global-text text-on-surface"}>{"Enter your name"}</Text>
                    <TextInput
                        className={"global-text-input border-on-surface-variant h-20 text-2xl text-on-surface-variant"}
                        id={"username"} onChangeText={setUsername}/>
                    <Text className={"global-text text-on-surface"}>{"Enter your email"}</Text>
                    <TextInput
                        className={"global-text-input border-on-surface-variant h-20 text-2xl text-on-surface-variant"}
                        id={"email"} onChangeText={setEmail}/>
                    <Text className={"global-text text-on-surface"}>{"Enter your password"}</Text>
                    <TextInput
                        className={"global-text-input border-on-surface-variant h-20 text-2xl text-on-surface-variant"}
                        secureTextEntry={true} id={"password"} onChangeText={setPassword}/>
                </View>
                <View className={"flex-1"}></View>
                <View className={"justify-between gap-4"}>
                    <TouchableOpacity onPress={createUserHandler
                    } className={"global-button  !bg-primary  "}>
                        <Text className={"global-text !text-on-primary "}>Submit</Text>
                    </TouchableOpacity>
                    <TouchableOpacity onPress={() => {
                        // for debugging
                        router.navigate("/loginPage")
                    }

                    } className={"global-button bg-primary-container"}>

                        <Text className={"global-text text-on-primary-container"}>Back to Login page</Text>
                    </TouchableOpacity>
                </View>
            </SafeAreaView>
        </>
    )

}

