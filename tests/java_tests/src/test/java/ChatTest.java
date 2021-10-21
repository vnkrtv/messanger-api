import java.io.IOException;
import java.io.InputStreamReader;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.concurrent.atomic.AtomicReference;

import dto.chat.ChatIdDto;
import dto.chat.CreateChatDto;
import org.apache.http.HttpStatus;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.ContentType;
import org.apache.http.entity.StringEntity;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

/**
 * @author senyasdr
 */
class ChatTest extends DbAbstractTest {

    @Test
    void createChat() throws IOException, URISyntaxException, InterruptedException {
        //when
        String chat = gson.toJson(new CreateChatDto("Pupkin chat"));
        HttpPost request = new HttpPost(getBasicURI().setPath("/v1/chats").build());
        request.setEntity(new StringEntity(chat, ContentType.APPLICATION_JSON));
        final AtomicReference<ChatIdDto> chatIdDto = new AtomicReference<>();
        try (CloseableHttpResponse resp = client.execute(request)) {
            //then
            Assertions.assertEquals(HttpStatus.SC_CREATED, resp.getStatusLine().getStatusCode());

            Assertions.assertDoesNotThrow(
                    () -> {
                        InputStreamReader streamReader = new InputStreamReader(resp.getEntity().getContent());
                        chatIdDto.set(gson.fromJson(streamReader, ChatIdDto.class));
                    }
            );
        }

        URI uri = getBasicURI().setPath(String.format("/v1/chats/%s/messages", chatIdDto.get().id))
                .addParameter("limit", "1").build();
        HttpGet getMsgReq = new HttpGet(uri);
        try (CloseableHttpResponse resp = client.execute(getMsgReq)) {
            Assertions.assertEquals(HttpStatus.SC_OK, resp.getStatusLine().getStatusCode());
        }
    }

    @Test
    void createChatWithSameName() throws IOException, URISyntaxException, InterruptedException {

        //given
        String chat = gson.toJson(new CreateChatDto("Pupkin chat"));
        HttpPost request = new HttpPost(getBasicURI().setPath("/v1/chats").build());
        request.setEntity(new StringEntity(chat, ContentType.APPLICATION_JSON));
        client.execute(request);

        //when
        try (CloseableHttpResponse resp = client.execute(request)) {

            //then
            Assertions.assertEquals(HttpStatus.SC_CREATED, resp.getStatusLine().getStatusCode());
        }
    }

    @Test
    void createSecondChat() throws IOException, URISyntaxException, InterruptedException {
        //given
        String chat = gson.toJson(new CreateChatDto("Pupkin chat"));
        HttpPost request = new HttpPost(getBasicURI().setPath("/v1/chats").build());
        request.setEntity(new StringEntity(chat, ContentType.APPLICATION_JSON));
        client.execute(request).close();

        //when
        chat = gson.toJson(new CreateChatDto("New chat"));
        request = new HttpPost(getBasicURI().setPath("/v1/chats").build());
        request.setEntity(new StringEntity(chat, ContentType.APPLICATION_JSON));
        try (CloseableHttpResponse resp = client.execute(request)) {

            //then
            Assertions.assertEquals(HttpStatus.SC_CREATED, resp.getStatusLine().getStatusCode());
        }
    }

}