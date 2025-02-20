{ pkgs }: {
  deps = [
    pkgs.geckodriver
    pkgs.python310Full
    pkgs.google-chrome
    pkgs.chromedriver
  ];
}
