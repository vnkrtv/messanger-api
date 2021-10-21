import java.io.IOException;
import java.io.InputStreamReader;
import java.net.URI;
import java.net.URISyntaxException;

import dto.chat.ChatIdDto;
import dto.chat.CreateChatDto;
import dto.message.CreateMessageDto;
import dto.message.MessageIdDto;
import dto.message.MessageList;
import dto.user.CreateUserDto;
import dto.user.UserIdDto;
import junit.framework.AssertionFailedError;
import org.apache.http.HttpResponse;
import org.apache.http.HttpStatus;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.ContentType;
import org.apache.http.entity.StringEntity;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.testcontainers.containers.wait.strategy.HostPortWaitStrategy;

/**
 * @author senyasdr
 */
class MessageTest extends DbAbstractTest {

    private String defaultChatId;
    private String defaultUserId;


    @BeforeEach
    void setUp() throws IOException, URISyntaxException, InterruptedException {
        super.setUp();
        defaultChatId = createChatWithName("pupkin chat").id;
        defaultUserId = createUser("Vasya Pupkin", defaultChatId).userId;
    }

    @Test
    void createMessage() throws IOException, URISyntaxException, InterruptedException {
        //when
        URI uri = getBasicURI().setPath(String.format("/v1/chats/%s/messages", defaultChatId))
                .addParameter("user_id", defaultUserId)
                .build();
        HttpPost req = new HttpPost(uri);
        String json = gson.toJson(new CreateMessageDto("Hello world"));
        req.setEntity(new StringEntity(json, ContentType.APPLICATION_JSON));
        try (CloseableHttpResponse resp = client.execute(req)) {

            ///then
            Assertions.assertEquals(HttpStatus.SC_CREATED, resp.getStatusLine().getStatusCode());
            Assertions.assertDoesNotThrow(
                    () -> gson.fromJson(new InputStreamReader(resp.getEntity().getContent()), MessageIdDto.class));
        }
    }

    @Test
    void createSameMessage() throws IOException, URISyntaxException, InterruptedException {
        //given
        URI uri = getBasicURI().setPath(String.format("/v1/chats/%s/messages", defaultChatId))
                .addParameter("user_id", defaultUserId)
                .build();
        HttpPost req = new HttpPost(uri);
        String json = gson.toJson(new CreateMessageDto("Hello world"));
        req.setEntity(new StringEntity(json, ContentType.APPLICATION_JSON));
        client.execute(req);

        //when
        try (CloseableHttpResponse resp = client.execute(req)) {

            ///then
            Assertions.assertEquals(HttpStatus.SC_CREATED, resp.getStatusLine().getStatusCode());
        }
    }

    @Test
    void createLongMessage() throws IOException, URISyntaxException {
        //when
        URI uri = getBasicURI().setPath(String.format("/v1/chats/%s/messages", defaultChatId))
                .addParameter("user_id", defaultUserId)
                .build();
        HttpPost req = new HttpPost(uri);
        String json = gson.toJson(new CreateMessageDto("To be, or not to be, that is the question:\n" +
                "Whether 'tis nobler in the mind to suffer\n" +
                "The slings and arrows of outrageous fortune,\n" +
                "Or to take arms against a sea of troubles\n" +
                "And by opposing end them. To die—to sleep,\n" +
                "No more; and by a sleep to say we end\n" +
                "The heart-ache and the thousand natural shocks\n" +
                "That flesh is heir to: 'tis a consummation\n" +
                "Devoutly to be wish'd. To die, to sleep;\n" +
                "To sleep, perchance to dream—ay, there's the rub:\n" +
                "For in that sleep of death what dreams may come,\n" +
                "When we have shuffled off this mortal coil,\n" +
                "Must give us pause—there's the respect\n" +
                "That makes calamity of so long life.\n" +
                "For who would bear the whips and scorns of time,\n" +
                "Th'oppressor's wrong, the proud man's contumely,\n" +
                "The pangs of dispriz'd love, the law's delay,\n" +
                "The insolence of office, and the spurns\n" +
                "That patient merit of th'unworthy takes,\n" +
                "When he himself might his quietus make\n" +
                "With a bare bodkin? Who would fardels bear,\n" +
                "To grunt and sweat under a weary life,\n" +
                "But that the dread of something after death,\n" +
                "The undiscovere'd country, from whose bourn\n" +
                "No traveller returns, puzzles the will,\n" +
                "And makes us rather bear those ills we have\n" +
                "Than fly to others that we know not of?\n" +
                "Thus conscience doth make cowards of us all,\n" +
                "And thus the native hue of resolution\n" +
                "Is sicklied o'er with the pale cast of thought,\n" +
                "And enterprises of great pith and moment\n" +
                "With this regard their currents turn awry\n" +
                "And lose the name of action."));
        req.setEntity(new StringEntity(json, ContentType.APPLICATION_JSON));
        try (CloseableHttpResponse resp = client.execute(req)) {

            ///then
            Assertions.assertEquals(HttpStatus.SC_CREATED, resp.getStatusLine().getStatusCode());
        }
    }

    @Test
    void createMessageFromAnotherUser() throws IOException, URISyntaxException {
        //given
        URI uri = getBasicURI().setPath(String.format("/v1/chats/%s/messages", defaultChatId))
                .addParameter("user_id", defaultUserId)
                .build();
        HttpPost req = new HttpPost(uri);
        String json = gson.toJson(new CreateMessageDto("Hello world"));
        req.setEntity(new StringEntity(json, ContentType.APPLICATION_JSON));
        client.execute(req);

        //when
        uri = getBasicURI().setPath(String.format("/v1/chats/%s/messages", defaultChatId))
                .addParameter("user_id", createUser("Test user", defaultChatId).userId)
                .build();

        req = new HttpPost(uri);
        json = gson.toJson(new CreateMessageDto("Hello world"));
        req.setEntity(new StringEntity(json, ContentType.APPLICATION_JSON));
        try (CloseableHttpResponse resp = client.execute(req)) {

            ///then
            Assertions.assertEquals(HttpStatus.SC_CREATED, resp.getStatusLine().getStatusCode());
        }
    }

    @Test
    void createMessageIncorrectChat() throws IOException, URISyntaxException {
        //when
        URI uri = getBasicURI().setPath(String.format("/v1/chats/%s/messages", "random_chat"))
                .addParameter("user_id", defaultUserId)
                .build();
        HttpPost req = new HttpPost(uri);
        String json = gson.toJson(new CreateMessageDto("Hello world"));
        req.setEntity(new StringEntity(json, ContentType.APPLICATION_JSON));
        try (CloseableHttpResponse resp = client.execute(req)) {

            ///then
            Assertions.assertEquals(HttpStatus.SC_NOT_FOUND, resp.getStatusLine().getStatusCode());
        }
    }

    @Test
    void createMessageIncorrectUser() throws IOException, URISyntaxException {
        //when
        URI uri = getBasicURI().setPath(String.format("/v1/chats/%s/messages", defaultChatId))
                .addParameter("user_id", "random_user")
                .build();
        HttpPost req = new HttpPost(uri);
        String json = gson.toJson(new CreateMessageDto("Hello world"));
        req.setEntity(new StringEntity(json, ContentType.APPLICATION_JSON));
        try (CloseableHttpResponse resp = client.execute(req)) {

            ///then
            Assertions.assertEquals(HttpStatus.SC_NOT_FOUND, resp.getStatusLine().getStatusCode());
        }
    }

    @Test
    void createMessageIncorrectBody() throws IOException, URISyntaxException {
        //when
        URI uri = getBasicURI().setPath(String.format("/v1/chats/%s/messages", defaultChatId))
                .addParameter("chat_id", defaultChatId)
                .addParameter("user_id", defaultUserId)
                .build();
        HttpPost req = new HttpPost(uri);
        try (CloseableHttpResponse resp = client.execute(req)) {

            ///then
            Assertions.assertEquals(HttpStatus.SC_BAD_REQUEST, resp.getStatusLine().getStatusCode());
        }
    }

    @ParameterizedTest
    @CsvSource({
            "5,  5",
            "10, 5",
            "5, 10",
            "0, 5"
    })
    void getMessagesFromChat(int messageCount, int limit) throws IOException, URISyntaxException {
        //given
        for (int i = 0; i < messageCount; i++) {
            createMessage("test message number " + i, defaultUserId, defaultChatId);
        }

        //when
        URI uri = getBasicURI().setPath(String.format("/v1/chats/%s/messages", defaultChatId))
                .addParameter("limit", String.valueOf(limit))
                .build();
        HttpGet req = new HttpGet(uri);
        try (CloseableHttpResponse resp = client.execute(req)) {

            ///then
            Assertions.assertEquals(HttpStatus.SC_OK, resp.getStatusLine().getStatusCode());
            MessageList messages =
                    gson.fromJson(new InputStreamReader(resp.getEntity().getContent()), MessageList.class);
            Assertions.assertEquals(Math.min(messageCount, limit), messages.messages.size());
        }
    }

    @Test
    void getMessagesFromChatNegativeLimit() throws IOException, URISyntaxException {
        //given
        for (int i = 0; i < 5; i++) {
            createMessage("test message number " + i, defaultUserId, defaultChatId);
        }

        //when
        URI uri = getBasicURI().setPath(String.format("/v1/chats/%s/messages", defaultChatId))
                .addParameter("limit", "-10")
                .build();
        HttpGet req = new HttpGet(uri);
        try (CloseableHttpResponse resp = client.execute(req)) {
            ///then
            Assertions.assertEquals(HttpStatus.SC_BAD_REQUEST, resp.getStatusLine().getStatusCode());
        }
    }

    @Test
    void getMessagesWithoutLimit() throws IOException, URISyntaxException {
        //given
        for (int i = 0; i < 5; i++) {
            createMessage("test message number " + i, defaultUserId, defaultChatId);
        }

        //when
        URI uri = getBasicURI().setPath(String.format("/v1/chats/%s/messages", defaultChatId))
                .build();
        HttpGet req = new HttpGet(uri);
        try (CloseableHttpResponse resp = client.execute(req)) {

            ///then
            Assertions.assertEquals(HttpStatus.SC_BAD_REQUEST, resp.getStatusLine().getStatusCode());
        }
    }

    @Test
    void getMessagesFromIncorrectChat() throws IOException, URISyntaxException {
        //given
        for (int i = 0; i < 5; i++) {
            createMessage("test message number " + i, defaultUserId, defaultChatId);
        }


        //when
        URI uri = getBasicURI().setPath(String.format("/v1/chats/%s/messages", "random_chat"))
                .addParameter("limit", "5")
                .build();
        HttpGet req = new HttpGet(uri);
        try (CloseableHttpResponse resp = client.execute(req)) {

            ///then
            Assertions.assertEquals(HttpStatus.SC_NOT_FOUND, resp.getStatusLine().getStatusCode());
        }
    }

    @Test
    void getMessagesWithOffset() throws IOException, URISyntaxException {
        //given
        for (int i = 0; i < 7; i++) {
            createMessage("test message number " + i, defaultUserId, defaultChatId);
        }
        URI uri = getBasicURI().setPath(String.format("/v1/chats/%s/messages", defaultChatId))
                .addParameter("limit", "5")
                .build();
        HttpGet req = new HttpGet(uri);
        MessageList messages;
        try (CloseableHttpResponse resp = client.execute(req)) {
            messages = gson.fromJson(new InputStreamReader(resp.getEntity().getContent()), MessageList.class);
        }

        //when
        uri = getBasicURI().setPath(String.format("/v1/chats/%s/messages", defaultChatId))
                .addParameter("limit", "5")
                .addParameter("from", messages.next.iterator)
                .build();
        req = new HttpGet(uri);
        try (CloseableHttpResponse resp = client.execute(req)) {
            MessageList offsetMessages =
                    gson.fromJson(new InputStreamReader(resp.getEntity().getContent()), MessageList.class);

            ///then
            Assertions.assertEquals(HttpStatus.SC_OK, resp.getStatusLine().getStatusCode());
            Assertions.assertEquals(2, offsetMessages.messages.size());
            Assertions.assertFalse(messages.messages.stream().anyMatch(offsetMessages.messages::contains));
        }
    }

    @Disabled("У нас нет гарантий на формат from. Поэтому оценивать его в тестах не можем.")
    @Test
    void getMessagesWithIncorrectOffset() throws IOException, URISyntaxException {
        //given
        for (int i = 0; i < 7; i++) {
            createMessage("test message number " + i, defaultUserId, defaultChatId);
        }

        //when
        URI uri = getBasicURI().setPath(String.format("/v1/chats/%s/messages", "random_chat"))
                .addParameter("limit", "5")
                .addParameter("from", "-1")
                .build();
        HttpGet req = new HttpGet(uri);
        try (CloseableHttpResponse resp = client.execute(req)) {

            ///then
            Assertions.assertEquals(HttpStatus.SC_BAD_REQUEST, resp.getStatusLine().getStatusCode());
        }
    }

    @Test
    void saveMessagesAndRebootServer() throws IOException, URISyntaxException {
        //given
        for (int i = 0; i < 5; i++) {
            createMessage("test message number " + i, defaultUserId, defaultChatId);
        }

        //when
        appContainer.stop();
        appContainer.start();
        appPort = appContainer.getMappedPort(8080);

        createMessage("message after reboot", defaultUserId, defaultChatId);


        //when
        URI uri = getBasicURI().setPath(String.format("/v1/chats/%s/messages", defaultChatId))
                .addParameter("limit", "10")
                .build();
        HttpGet req = new HttpGet(uri);
        try (CloseableHttpResponse resp = client.execute(req)) {


            ///then
            MessageList messages =
                    gson.fromJson(new InputStreamReader(resp.getEntity().getContent()), MessageList.class);
            Assertions.assertEquals(HttpStatus.SC_OK, resp.getStatusLine().getStatusCode());
            Assertions.assertEquals(6, messages.messages.size());
        }
    }

    private MessageIdDto createMessage(String text, String userId, String chatId) throws URISyntaxException,
            IOException
    {
        URI uri = getBasicURI().setPath(String.format("/v1/chats/%s/messages", defaultChatId))
                .addParameter("chat_id", chatId)
                .addParameter("user_id", userId)
                .build();
        HttpPost req = new HttpPost(uri);
        String json = gson.toJson(new CreateMessageDto(text));
        req.setEntity(new StringEntity(json, ContentType.APPLICATION_JSON));

        try (CloseableHttpResponse resp = client.execute(req)) {
            return gson.fromJson(new InputStreamReader(resp.getEntity().getContent()), MessageIdDto.class);
        }
    }

    private ChatIdDto createChatWithName(String chatName) throws URISyntaxException, IOException {
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

    private UserIdDto createUser(String username, String chatId) throws IOException, URISyntaxException {
        URI uri = getBasicURI().setPath(String.format("/v1/chats/%s/users", chatId)).build();
        HttpPost req = new HttpPost(uri);
        String json = gson.toJson(new CreateUserDto(username));
        req.setEntity(new StringEntity(json, ContentType.APPLICATION_JSON));
        try (CloseableHttpResponse resp = client.execute(req)) {
            int statusCode = resp.getStatusLine().getStatusCode();
            if (statusCode < 200 || statusCode >= 300) {
                throw new AssertionFailedError("Incorrect response status code while creating user: " + statusCode + ".");
            }
            return gson.fromJson(new InputStreamReader(resp.getEntity().getContent()), UserIdDto.class);
        }
    }

}