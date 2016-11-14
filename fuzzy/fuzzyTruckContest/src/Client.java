
public class Client {
	public static void main() {
	 try{
	     socket = new Socket("kq6py", 4321);
	     out = new PrintWriter(socket.getOutputStream(), 
	                 true);
	     in = new BufferedReader(new InputStreamReader(
	                socket.getInputStream()));
	   } catch (UnknownHostException e) {
	     System.out.println("Unknown host: kq6py");
	     System.exit(1);
	   } catch  (IOException e) {
	     System.out.println("No I/O");
	     System.exit(1);
	   }
	}
}
