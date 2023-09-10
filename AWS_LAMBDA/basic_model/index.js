import OpenAI from 'openai';
left to figure out the delivery, database update and safety + security measures.


const openai = new OpenAI({
	organization: process.env.OPEN_AI_ORGANISATION,
	apiKey: process.env.OPEN_AI_API_KEY
});
/* global awslambda */
export const handler = awslambda.streamifyResponse(
  async (event, responseStream, _context) => {
    try {
      const body = event.body;
      const messages = JSON.parse(body).chatLog;
      const functions = JSON.parse(body).functions;
      const response = await openai.chat.completions.create({
        model: "gpt-4",
	temperature: 0.1,
        messages: messages,
	functions: functions,
        stream: true,
      });

      responseStream.setContentType("text/plain");
      for await (const chunk of response) {
		responseStream.write(chunk.choices[0].delta.content);
      }
      responseStream.end();

    } catch (error) {
      // Handle errors here and potentially send an error response
      console.error(error);
    }
  }
);

