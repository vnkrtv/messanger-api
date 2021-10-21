package dto.user;

import com.google.gson.annotations.SerializedName;

/**
 * @author senyasdr
 */
public class CreateUserDto {

    @SerializedName("user_name")
    public final String username;

    public CreateUserDto(String username) {
        this.username = username;
    }
}
