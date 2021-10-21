package dto.chat;

import com.google.gson.annotations.SerializedName;

/**
 * @author senyasdr
 */
public class CreateChatDto {

    @SerializedName("chat_name")
    public final String chatName;

    public CreateChatDto(String chatName) {
        this.chatName = chatName;
    }
}
