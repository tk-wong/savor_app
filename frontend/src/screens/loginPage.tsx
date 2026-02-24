import {Text, TextInput, View, TouchableOpacity, StyleSheet, Alert} from "react-native";
import * as Speech from 'expo-speech';
import {useState} from "react";
import {useRouter} from 'expo-router';

export default function LoginPage() {
    const [username, setUsername] = useState("")
    const [password, setPassword] = useState("")
    const speak = () => {
        const thingToSay = 'testing 123';
        Speech.speak(thingToSay,
            {language: "en-US",
            rate: 0.8,});
    };

    const router = useRouter();
    return (
        <View
            style={{
                flex: 1,
                justifyContent: "center",
                alignItems: "center",
            }}
        >
            <Text>Welcome</Text>
            <Text>User Name:</Text>
            <TextInput style={{borderWidth: 1}} placeholder={"User name"} onChangeText={setUsername}
                       id={"username_input"}/>
            <Text>Password</Text>
            <TextInput style={{borderWidth: 1}} secureTextEntry={true} placeholder={"Password"}
                       onChangeText={setPassword} id={"password_input"}/>
            <TouchableOpacity onPress={() => {
                Alert.alert("User information", `name: ${username}, password: ${password}`);
            }} style={style.button}>
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
                router.navigate("/chatPage")
            }
            } style={style.button}>
                <Text>Chat page</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={speak} style={style.button}>
                <Text>Press to test speech</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={()=> {
                // for debugging
                router.navigate("/allRecipePage")
            }

            } style={style.button}>

                <Text>All recipes page</Text>
            </TouchableOpacity>
        </View>
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
