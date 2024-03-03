{
  description = "a leaderboard to your group chat";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/release-23.11";
  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.poetry2nix = {
    url = "github:nix-community/poetry2nix";
    inputs.nixpkgs.follows = "nixpkgs";
    inputs.systems.follows = "flake-utils/systems";
    inputs.flake-utils.follows = "flake-utils";
  };

  inputs.flake-compat.url = "https://flakehub.com/f/edolstra/flake-compat/1.0.1.tar.gz";

  outputs = inputs@{ self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        poetry2nix = inputs.poetry2nix.lib.mkPoetry2Nix { inherit pkgs; };

        pkgs = nixpkgs.legacyPackages.${system};

        fixups = poetry2nix.overrides.withDefaults (self: super: {
          psutil = super.psutil.overridePythonAttrs (_old: {
            # fixes for building psutils 5.9.8 on MacOS/darwin: https://github.com/giampaolo/psutil/pull/2364
            # - fixes build failure for missing include <CoreFoundation>
            # - fixes build failure for missing include net/if_dl.h
            src = pkgs.fetchFromGitHub {
              owner = "ryandesign";
              repo = "psutil";
              rev = "aee7739668b6a28326e4f50fec346c3bfbe2d887";
              hash = "sha256-dNriB5tgXulKmR2iQrnYN714Oz92bQB3wgEImXefQCI=";
            };
          });
        });
      in
      {
        packages = {
          telegram-leaderboard-bot = poetry2nix.mkPoetryApplication {
            projectDir = self;
            overrides = fixups;
          };
          default = self.packages.${system}.telegram-leaderboard-bot;
        };

        devShells = {
          telegram-leaderboard-bot = pkgs.mkShell {
            packages = [
              pkgs.poetry
              (poetry2nix.mkPoetryEnv {
                projectDir = self;
                overrides = fixups;
              })
            ];
          };

          default = self.devShells.${system}.telegram-leaderboard-bot;
        };
      }
    );
}
