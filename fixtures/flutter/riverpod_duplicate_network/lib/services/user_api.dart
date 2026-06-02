abstract class UserApi {
  Future<String> fetchUser();
}

class CountingUserApi implements UserApi {
  int calls = 0;

  @override
  Future<String> fetchUser() async {
    calls++;
    return 'user-$calls';
  }
}
