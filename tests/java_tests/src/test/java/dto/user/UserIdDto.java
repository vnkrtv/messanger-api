package dto.user;

import com.google.gson.annotations.SerializedName;

/**
 * @author senyasdr
 */
public class UserIdDto {

    @SerializedName("user_id")
    public final String userId;

    public UserIdDto(String userId) {
        this.userId = userId;
    }
}
