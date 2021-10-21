package dto.message;

import com.google.gson.annotations.SerializedName;

/**
 * @author senyasdr
 */
public class MessageIdDto {

    @SerializedName("message_id")
    public final String id;

    public MessageIdDto(String id) {
        this.id = id;
    }
}
