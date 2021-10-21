import java.io.IOException;
import java.io.InputStreamReader;
import java.net.URI;
import java.net.URISyntaxException;

import dto.chat.ChatIdDto;
import dto.chat.CreateChatDto;
import dto.user.CreateUserDto;
import junit.framework.AssertionFailedError;
import org.apache.http.HttpResponse;
import org.apache.http.HttpStatus;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.ContentType;
import org.apache.http.entity.StringEntity;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/**
 * @author senyasdr
 */
class UserTest extends DbAbstractTest {

    private String defaultChatId;

    @BeforeEach
    void setUp() throws IOException, URISyntaxException, InterruptedException {
        super.setUp();
        defaultChatId = createChatWithName("Pupkin chat").id;
    }

    @Test
    void addUserToExistingChat() throws IOException, URISyntaxException, InterruptedException {
        //when
        URI uri = getBasicURI().setPath(String.format("/v1/chats/%s/users", defaultChatId)).build();
        HttpPost req = new HttpPost(uri);
        String json = gson.toJson(new CreateUserDto("Vasya Pupkin"));
        req.setEntity(new StringEntity(json, ContentType.APPLICATION_JSON));
        HttpResponse resp = client.execute(req);

        //then
        Assertions.assertEquals(HttpStatus.SC_CREATED, resp.getStatusLine().getStatusCode());
    }

    @Test
    void addUserToExistingChatAgain() throws IOException, URISyntaxException, InterruptedException {
        //when
        URI uri = getBasicURI().setPath(String.format("/v1/chats/%s/users", defaultChatId)).build();
        HttpPost req = new HttpPost(uri);
        String json = gson.toJson(new CreateUserDto("Vasya Pupkin"));
        req.setEntity(new StringEntity(json, ContentType.APPLICATION_JSON));
        HttpResponse resp = client.execute(req);

        //then
        Assertions.assertEquals(HttpStatus.SC_CREATED, resp.getStatusLine().getStatusCode());
    }

    @Test
    void addUserToNotExistingChat() throws IOException, URISyntaxException, InterruptedException {
        //when
        URI uri = getBasicURI().setPath(String.format("/v1/chats/%s/users", "random_chat")).build();
        HttpPost req = new HttpPost(uri);
        String json = gson.toJson(new CreateUserDto("Vasya Pupkin"));
        req.setEntity(new StringEntity(json, ContentType.APPLICATION_JSON));
        HttpResponse resp = client.execute(req);

        //then
        Assertions.assertEquals(HttpStatus.SC_NOT_FOUND, resp.getStatusLine().getStatusCode());
    }

    @Test
    void addUserWithoutBodyChat() throws IOException, URISyntaxException, InterruptedException {
        //when
        URI uri = getBasicURI().setPath(String.format("/v1/chats/%s/users", defaultChatId)).build();
        HttpPost req = new HttpPost(uri);
        HttpResponse resp = client.execute(req);

        //then
        Assertions.assertEquals(HttpStatus.SC_BAD_REQUEST, resp.getStatusLine().getStatusCode());
    }

    private ChatIdDto createChatWithName(String chatName) throws URISyntaxException, IOException, InterruptedException {
        String chat = gson.toJson(new CreateChatDto(chatName));
        HttpPost request = new HttpPost(getBasicURI().setPath("/v1/chats").build());
        request.setEntity(new StringEntity(chat, ContentType.APPLICATION_JSON));
        try (CloseableHttpResponse resp = client.execute(request)) {

            int statusCode = resp.getStatusLine().getStatusCode();
            if (statusCode < 200 || statusCode >= 300) {
                throw new AssertionFailedError("Incorrect response status code while creating chat: " + statusCode + ".");
            }
            return gson.fromJson(new InputStreamReader(resp.getEntity().getContent()), ChatIdDto.class);
        }
    }
}
