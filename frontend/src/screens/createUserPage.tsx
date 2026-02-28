import { ScrollView, Text, TextInput, TouchableOpacity, Alert, StyleSheet } from "react-native";
import { Stack, useRouter } from "expo-router";

export default function CreateUserPage() {
    const router = useRouter();
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
                <TextInput style={{ borderWidth: 1 }} id={"username"} />
                <Text>{"Enter your email"}</Text>
                <TextInput style={{ borderWidth: 1 }} id={"email"} />
                <Text>{"Enter your password"}</Text>
                <TextInput style={{ borderWidth: 1 }} secureTextEntry={true} id={"password"} />
                <TouchableOpacity onPress={() => {
                    // TODO: handle create user logic here, for now just show an alert with the entered username, email and password
                    Alert.alert("User created", "Creating user...");
                }} style={style.button}>
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
const style = StyleSheet.create(
    {
        button: {
            alignItems: 'center',
            backgroundColor: '#DDDDDD',
            padding: 10,
        },
    }
)
