package dto.message;

import java.util.List;

/**
 * @author senyasdr
 */
public class MessageList {

    public final List<MessageDto> messages;
    public final Cursor next;

    public MessageList(List<MessageDto> messages, Cursor next) {
        this.messages = messages;
        this.next = next;
    }
}
