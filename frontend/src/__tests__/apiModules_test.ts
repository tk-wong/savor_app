import axios from "axios";
import * as SecureStore from "expo-secure-store";
import { ApiRequestError, mapApiError } from "../api/apiRequestError";
import apiClient from "../api/client";
import { login, createUser } from "../api/auth";
import {
  sendMessage,
  getAllChatGroups,
  getChatHistoryByGroupId,
  getNewChatGroup,
} from "../api/chat";
import { getAllRecipes, getRecipeById } from "../api/recipe";

jest.mock("../api/client", () => ({
  __esModule: true,
  default: {
    post: jest.fn(),
    get: jest.fn(),
  },
}));

jest.mock("expo-secure-store", () => ({
  setItemAsync: jest.fn(),
  getItemAsync: jest.fn(),
  deleteItemAsync: jest.fn(),
}));

describe("apiRequestError mapping", () => {
  const mockedAxios = axios as jest.Mocked<typeof axios>;

  beforeEach(() => {
    jest.clearAllMocks();
    jest
      .spyOn(mockedAxios, "isAxiosError")
      .mockImplementation((error: unknown) => Boolean((error as any)?.isAxiosError));
  });

  it("maps all explicit status codes and defaults", () => {
    const knownStatusCases: Array<{ status: number; expectedMessage: string; serverMessage?: string }> = [
      { status: 400, expectedMessage: "from server", serverMessage: "from server" },
      { status: 401, expectedMessage: "Unauthorized. Please sign in again." },
      { status: 403, expectedMessage: "Forbidden." },
      { status: 404, expectedMessage: "Resource not found." },
      { status: 409, expectedMessage: "Conflict error." },
      { status: 422, expectedMessage: "Validation failed." },
      { status: 429, expectedMessage: "Too many requests. Try again shortly." },
    ];

    knownStatusCases.forEach(({ status, expectedMessage, serverMessage }) => {
      const mapped = mapApiError({
        isAxiosError: true,
        response: { status, data: { message: serverMessage } },
      });

      expect(mapped).toBeInstanceOf(ApiRequestError);
      expect(mapped.message).toBe(expectedMessage);
      expect(mapped.status).toBe(status);
      expect(mapped.details).toBeDefined();
    });

    const fiveHundred = mapApiError({ isAxiosError: true, response: { status: 503, data: {} } });
    expect(fiveHundred.message).toBe("Server error. Please try again.");
    expect(fiveHundred.status).toBe(503);

    const noStatus = mapApiError({
      isAxiosError: true,
      response: { status: undefined, data: { message: "transport issue" } },
    });
    expect(noStatus.message).toBe("transport issue");
    expect(noStatus.status).toBeUndefined();

    const nonAxios = mapApiError(new Error("no axios context"));
    expect(nonAxios.message).toBe("Unexpected error.");
    expect(nonAxios.status).toBeUndefined();
  });

  it("covers case 400 with no server message fallback", () => {
    const mapped = mapApiError({
      isAxiosError: true,
      response: { status: 400, data: {} },
    });

    expect(mapped.message).toBe("Bad request.");
    expect(mapped.status).toBe(400);
  });

  it("covers case 422 with server message", () => {
    const mapped = mapApiError({
      isAxiosError: true,
      response: { status: 422, data: { message: "Validation error from server" } },
    });

    expect(mapped.message).toBe("Validation error from server");
    expect(mapped.status).toBe(422);
  });

  it("covers default case with no server message fallback", () => {
    const mapped = mapApiError({
      isAxiosError: true,
      response: { status: 418, data: {} },
    });

    expect(mapped.message).toBe("Network/API error.");
    expect(mapped.status).toBe(418);
  });
});

describe("auth api", () => {
  const mockedApiClient = apiClient as jest.Mocked<typeof apiClient>;
  const mockedSetItemAsync = SecureStore.setItemAsync as jest.Mock;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("logs in, stores token, and returns response payload", async () => {
    mockedApiClient.post.mockResolvedValue({
      data: { user: { access_token: "token-123" }, profile: { id: 1 } },
    } as any);

    const result = await login("user@example.com", "secret");

    expect(mockedApiClient.post).toHaveBeenCalledWith("/user/login", {
      email: "user@example.com",
      password: "secret",
    });
    expect(mockedSetItemAsync).toHaveBeenCalledWith("userToken", "token-123");
    expect(result).toEqual({ user: { access_token: "token-123" }, profile: { id: 1 } });
  });

  it("maps login failures to ApiRequestError", async () => {
    mockedApiClient.post.mockRejectedValue({
      isAxiosError: true,
      response: { status: 500, data: {} },
    });

    await expect(login("user@example.com", "bad")).rejects.toMatchObject({
      name: "ApiRequestError",
      message: "Server error. Please try again.",
      status: 500,
    });
  });

  it("creates user and returns payload", async () => {
    mockedApiClient.post.mockResolvedValue({ data: { id: 7, username: "new_user" } } as any);

    const result = await createUser("new@example.com", "new_user", "pass123");

    expect(mockedApiClient.post).toHaveBeenCalledWith("/user/create", {
      email: "new@example.com",
      username: "new_user",
      password: "pass123",
    });
    expect(result).toEqual({ id: 7, username: "new_user" });
  });

  it("maps create user failures to ApiRequestError", async () => {
    mockedApiClient.post.mockRejectedValue({
      isAxiosError: true,
      response: { status: 409, data: {} },
    });

    await expect(createUser("existing@example.com", "existing", "pass123")).rejects.toMatchObject({
      name: "ApiRequestError",
      message: "Conflict error.",
      status: 409,
    });
  });
});

describe("chat api", () => {
  const mockedApiClient = apiClient as jest.Mocked<typeof apiClient>;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("sends message with expected payload and timeout", async () => {
    mockedApiClient.post.mockResolvedValue({ data: { chat_reply: "Hi" } } as any);

    const result = await sendMessage("Hello", 55);

    expect(mockedApiClient.post).toHaveBeenCalledWith(
      "/chat",
      { prompt: "Hello", chat_group_id: 55 },
      { timeout: 120000 },
    );
    expect(result).toEqual({ chat_reply: "Hi" });
  });

  it("loads new group, all groups, and group history", async () => {
    mockedApiClient.get
      .mockResolvedValueOnce({ data: { group_id: 123 } } as any)
      .mockResolvedValueOnce({ data: { chat_groups: [{ id: 1 }] } } as any)
      .mockResolvedValueOnce({ data: { chat_history: [{ role: "user", content: "hello" }] } } as any);

    await expect(getNewChatGroup()).resolves.toEqual({ group_id: 123 });
    await expect(getAllChatGroups()).resolves.toEqual({ chat_groups: [{ id: 1 }] });
    await expect(getChatHistoryByGroupId(1)).resolves.toEqual([{ role: "user", content: "hello" }]);

    expect(mockedApiClient.get).toHaveBeenNthCalledWith(1, "/chat/group/new");
    expect(mockedApiClient.get).toHaveBeenNthCalledWith(2, "/chat/group/all");
    expect(mockedApiClient.get).toHaveBeenNthCalledWith(3, "/chat/group/1/history");
  });

  it("maps sendMessage failures", async () => {
    mockedApiClient.post.mockRejectedValue({
      isAxiosError: true,
      response: { status: 422, data: {} },
    });

    await expect(sendMessage("prompt", 7)).rejects.toMatchObject({
      name: "ApiRequestError",
      message: "Validation failed.",
      status: 422,
    });
  });

  it("maps getNewChatGroup failures", async () => {
    mockedApiClient.get.mockRejectedValue({
      isAxiosError: true,
      response: { status: 429, data: {} },
    });

    await expect(getNewChatGroup()).rejects.toMatchObject({
      name: "ApiRequestError",
      message: "Too many requests. Try again shortly.",
      status: 429,
    });
  });

  it("maps getAllChatGroups failures", async () => {
    mockedApiClient.get.mockRejectedValue({
      isAxiosError: true,
      response: { status: 404, data: {} },
    });

    await expect(getAllChatGroups()).rejects.toMatchObject({
      name: "ApiRequestError",
      message: "Resource not found.",
      status: 404,
    });
  });

  it("maps getChatHistoryByGroupId failures", async () => {
    mockedApiClient.get.mockRejectedValue({
      isAxiosError: true,
      response: { status: 401, data: {} },
    });

    await expect(getChatHistoryByGroupId(999)).rejects.toMatchObject({
      name: "ApiRequestError",
      message: "Unauthorized. Please sign in again.",
      status: 401,
    });
  });
});

describe("recipe api", () => {
  const mockedApiClient = apiClient as jest.Mocked<typeof apiClient>;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("fetches all recipes and recipe by id", async () => {
    mockedApiClient.get
      .mockResolvedValueOnce({ data: { recipes: [{ id: 1, title: "Pasta" }] } } as any)
      .mockResolvedValueOnce({ data: { id: 9, title: "Soup" } } as any);

    await expect(getAllRecipes()).resolves.toEqual({ recipes: [{ id: 1, title: "Pasta" }] });
    await expect(getRecipeById(9)).resolves.toEqual({ id: 9, title: "Soup" });

    expect(mockedApiClient.get).toHaveBeenNthCalledWith(1, "/recipes");
    expect(mockedApiClient.get).toHaveBeenNthCalledWith(2, "/recipes/9");
  });

  it("maps getAllRecipes failures", async () => {
    mockedApiClient.get.mockRejectedValue({
      isAxiosError: true,
      response: { status: 403, data: {} },
    });

    await expect(getAllRecipes()).rejects.toMatchObject({
      name: "ApiRequestError",
      message: "Forbidden.",
      status: 403,
    });
  });

  it("maps getRecipeById failures", async () => {
    mockedApiClient.get.mockRejectedValue({
      isAxiosError: true,
      response: { status: 400, data: { message: "recipe id invalid" } },
    });

    await expect(getRecipeById(0)).rejects.toMatchObject({
      name: "ApiRequestError",
      message: "recipe id invalid",
      status: 400,
    });
  });
});


