import {Text, TextInput, View} from "react-native";

export default function Index() {
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
        <TextInput style={{borderWidth: 1}}/>
        <Text>Password</Text>
        <TextInput style={{borderWidth: 1}} secureTextEntry={true}/>
        <button onClick={()=>{alert("submit")}}>submit</button>
        <button onClick={()=>{alert("Create account")}}>Create account</button>
    </View>
  );
}
