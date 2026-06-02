String? validatePassword(String password) {
  if (password.isEmpty) {
    return 'Enter a password';
  }
  return null;
}
