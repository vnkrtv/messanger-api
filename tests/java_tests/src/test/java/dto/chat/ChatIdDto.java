package dto.chat;

import com.google.gson.annotations.SerializedName;

/**
 * @author senyasdr
 */
public class ChatIdDto {
    @SerializedName("chat_id")
    public final String id;

    public ChatIdDto(String id) {
        this.id = id;
    }
}
