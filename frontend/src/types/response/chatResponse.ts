import { DetailRecipe } from "../index";

export interface QuestionResponse {
  prompt_type: "question";
  answer: string;
}

export interface RecipeResponse {
  prompt_type: "recipe";
  recipe: DetailRecipe;
}
export type ChatResponse = QuestionResponse | RecipeResponse;
