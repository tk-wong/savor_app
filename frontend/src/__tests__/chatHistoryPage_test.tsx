import { Alert } from "react-native";
import { fireEvent, render, screen, waitFor } from "@testing-library/react-native";
import ChatHistoryPage from "../screens/chatHistoryPage";
import { getAllChatGroups } from "../api/chat";
import { useFocusEffect, useRouter } from "expo-router";

jest.mock("../api/chat");
jest.mock("expo-router");
// Use manual mock file to replace FlatList internals without inline factory closure.
// jest.mock("react-native/Libraries/Lists/FlatList");

describe("ChatHistoryPage", () => {
  const mockedGetAllChatGroups = getAllChatGroups as jest.MockedFunction<typeof getAllChatGroups>;
  const mockedUseRouter = useRouter as jest.Mock;
  const mockedUseFocusEffect = useFocusEffect as jest.Mock;
  const pushMock = jest.fn();
  const alertMock = jest.spyOn(Alert, "alert");

  beforeEach(() => {
    jest.clearAllMocks();
    mockedUseRouter.mockReturnValue({ push: pushMock });
    mockedUseFocusEffect.mockImplementation((effect: () => void) => {
      effect();
    });
  });

  afterAll(() => {
    alertMock.mockRestore();
  });

  it("fetches and renders chat groups", async () => {
    mockedGetAllChatGroups.mockResolvedValue({
      chat_groups: [
        { id: 1, name: "Dinner Plan", last_edited: "2026-03-20T12:00:00Z" },
        { id: 2, name: "Weekend Meals", last_edited: "2026-03-21T08:30:00Z" },
      ],
    } as any);

    render(<ChatHistoryPage />);

    await waitFor(() => {
      expect(screen.getByText("Dinner Plan")).toBeTruthy();
      expect(screen.getByText("Weekend Meals")).toBeTruthy();
    });
  });

  it("formats last_edit dates and falls back for invalid date strings", async () => {
    mockedGetAllChatGroups.mockResolvedValue({
      chat_groups: [
        { id: 7, name: "Valid Date", last_edit: "2026-03-20T12:00:00Z" },
        { id: 8, name: "Invalid Date", last_edit: "not-a-date" },
      ],
    } as any);

    render(<ChatHistoryPage />);

    await waitFor(() => {
      expect(screen.getByText("Valid Date")).toBeTruthy();
      expect(screen.getByText("20th, Mar 2026")).toBeTruthy();
      expect(screen.getByText("Invalid Date")).toBeTruthy();
    });

    const unknownDateRows = screen.getAllByText("Unknown date");
    expect(unknownDateRows.length).toBeGreaterThan(0);
  });

  it("navigates to chat page with chatGroupId when a group is pressed", async () => {
    mockedGetAllChatGroups.mockResolvedValue({
      chat_groups: [{ id: 42, name: "Group 42", last_edited: "2026-03-21T08:30:00Z" }],
    } as any);

    render(<ChatHistoryPage />);

    await waitFor(() => {
      expect(screen.getByText("Group 42")).toBeTruthy();
    });

    fireEvent.press(screen.getByText("Group 42"));

    expect(pushMock).toHaveBeenCalledWith({ pathname: "/chatPage", params: { chatGroupId: 42 } });
  });

  it("shows fallback error details when request fails", async () => {
    mockedGetAllChatGroups.mockRejectedValue({});

    render(<ChatHistoryPage />);

    await waitFor(() => {
      expect(alertMock).toHaveBeenCalledWith(
        "Error: Unknown",
        "Unknown error occurred while fetching chat groups.",
      );
    });
  });
});
