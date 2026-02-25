import { router, useLocalSearchParams } from "expo-router";
import { Image, ImageSourcePropType, Text, TouchableOpacity } from "react-native";
import { ScrollView } from "react-native";
import { SafeAreaProvider, SafeAreaView } from "react-native-safe-area-context";

interface SampleDetailRecipe {
    id: number;
    name: string;
    description: string;
    image: ImageSourcePropType;
    ingredients: string[];
    instructions: string[];
    tips: string[];
}

export default function RecipePage() {
    const recipe: SampleDetailRecipe = {
        id: 1,
        name: "Spaghetti Carbonara",
        description: "A classic Italian pasta dish made with eggs, cheese, pancetta, and black pepper.",
        image: require("../../assets/images/react-logo.png"),
        ingredients: [
            "200g spaghetti",
            "100g pancetta",
            "2 large eggs",
            "50g pecorino cheese",
            "50g parmesan cheese",
            "2 cloves of garlic",
            "Salt and black pepper to taste"
        ],
        instructions: [
            "Cook the spaghetti in a large pot of salted boiling water until al dente.",
            "In a pan, cook the pancetta with the garlic until crispy. Remove the garlic and discard.",
            "In a bowl, beat the eggs and mix in the pecorino and parmesan cheese.",
            "Drain the spaghetti and add it to the pan with the pancetta. Remove from heat.",
            "Quickly pour the egg and cheese mixture over the pasta, tossing quickly to prevent scrambling.",
            "Season with salt and black pepper to taste. Serve immediately."
        ],
        tips: [
            "Use fresh eggs for the best flavor and texture.",
            "Pecorino cheese adds a sharper flavor, while parmesan is milder. You can adjust the ratio to your taste.",
            "Make sure to toss the pasta quickly with the egg mixture to create a creamy sauce without scrambling the eggs."
        ]
    };
    const params = useLocalSearchParams();
    console.log(`Received recipe id: ${params.id}`);
    // TODO: fetch recipe details from backend and display it in a card format
    return (
        <SafeAreaView>
            <ScrollView>
                <Text>{recipe.name}</Text>
                <Image source={recipe.image} style={{ width: 200, height: 200 }} />
                <Text>{recipe.description}</Text>
                <Text>Ingredients:</Text>
                {recipe.ingredients.map((ingredient, index) => (
                    <Text key={index}>{ingredient}</Text>
                ))}
                <Text>Instructions:</Text>
                {recipe.instructions.map((instruction, index) => (
                    <Text key={index}>{`${index + 1}. ${instruction}`}</Text>
                ))}
                <Text>Tips:</Text>
                {recipe.tips.map((tip, index) => (
                    <Text key={index}>{`${index + 1}. ${tip}`}</Text>
                ))}
                <TouchableOpacity onPress={() => {
                    console.log(`turn on voice assistant to read the recipe ${recipe.name} (id: ${recipe.id})`);
                }}
                    style={{ backgroundColor: "blue", padding: 10, margin: 10, borderRadius: 5 }}>
                    <Text style={{ color: "white" }}>Voice Interaction</Text>
                </TouchableOpacity>
                <TouchableOpacity onPress={() => {
                    router.back();
                }}                    style={{ backgroundColor: "green", padding: 10, margin: 10, borderRadius: 5 }}>
                    <Text style={{ color: "white" }}>return to all recipe</Text>
                </TouchableOpacity>
            </ScrollView>
        </SafeAreaView>
    )
}