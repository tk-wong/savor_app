import {ScrollView, View, Text, TextInput, TouchableOpacity, Alert, StyleSheet} from "react-native";
import {Stack} from "expo-router";
import {useState} from "react";
import {inspect} from "node:util";

class User{
    name: string;
    email: string;
    password: string
    constructor(name: string, email: string, password: string) {
        this.name = name;
        this.email = email;
        this.password = password;
    }
}

export default function CreateUserPage() {
    const [user,setUser] = useState<User>();
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
                <TextInput style={{borderWidth: 1}} id={"username"}/>
                <Text>{"Enter your email"}</Text>
                <TextInput style={{borderWidth: 1}} id={"email"}/>
                <Text>{"Enter your password"}</Text>
                <TextInput style={{borderWidth: 1}} secureTextEntry={true} id={"password"}/>
                <TouchableOpacity onPress={() => {
                    Alert.alert("User created","Creating user...");
                }} style={style.button}>
                    <Text>Submit</Text>
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