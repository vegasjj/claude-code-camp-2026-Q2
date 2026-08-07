# BoukenshaLoader resolves which step folder to load from, then boots the REPL.
#
# Resolution order for BOUKENSHA_PATH (which step lib to load):
#   1. BOUKENSHA_PATH environment variable
#   2. BOUKENSHA_PATH key in ~/.boukensharc
#   3. A bare path in ~/.boukensharc (backwards-compatible single-line format)
#   4. The lib/ directory bundled inside this gem (step 10 — the latest release)
#
# Resolution order for BOUKENSHA_DIR (config directory):
#   1. BOUKENSHA_DIR environment variable
#   2. BOUKENSHA_DIR key in ~/.boukensharc
#   3. ~/.boukensha  (default)
#
# ~/.boukensharc format (key=value, one per line):
#   BOUKENSHA_PATH=~/Sites/boukensha/07_the_repl_loop
#   BOUKENSHA_DIR=~/projects/mybot/.boukensha
#
# A bare path (no key=) is treated as BOUKENSHA_PATH for backwards compat:
#   ~/Sites/boukensha/07_the_repl_loop
#
# MUD connection details come from settings.yaml (mud: block) by default.
# The legacy MUD_NAME / MUD_HOST / MUD_PORT / MUD_PASSWORD env vars are still
# honoured and take precedence over config when set.
#
# Examples:
#   boukensha                                                              # uses bundled lib + ~/.boukensha
#   BOUKENSHA_PATH=~/Sites/boukensha/04_api_client boukensha              # loads step 4
#   BOUKENSHA_DIR=~/projects/mybot/.boukensha boukensha                   # custom config dir
#   echo "BOUKENSHA_PATH=~/Sites/boukensha/10_standard_tool_library" > ~/.boukensharc && boukensha
module BoukenshaLoader
  # Absolute path to this gem's own bundled boukensha lib.
  BUNDLED_LIB = File.expand_path("../boukensha.rb", __FILE__)

  RC_PATH = File.expand_path("~/.boukensharc").freeze

  # Parse ~/.boukensharc and return a hash with :boukensha_path and :boukensha_dir.
  # Supports two formats:
  #   - Key=value lines:  BOUKENSHA_PATH=~/some/path
  #   - Bare path (legacy): treated as BOUKENSHA_PATH
  # Lines starting with # are comments. Blank lines are ignored.
  def self.parse_rc
    return {} unless File.exist?(RC_PATH)

    values = {}
    File.readlines(RC_PATH).each do |line|
      line = line.strip
      next if line.empty? || line.start_with?("#")

      if line =~ /\ABOUKENSHA_PATH\s*=\s*(.+)\z/
        values[:boukensha_path] = $1.strip
      elsif line =~ /\ABOUKENSHA_DIR\s*=\s*(.+)\z/
        values[:boukensha_dir] = $1.strip
      else
        # Bare path — backwards compat: treat as BOUKENSHA_PATH
        values[:boukensha_path] ||= line
      end
    end

    values
  end

  # Returns the BOUKENSHA_DIR from ~/.boukensharc, or nil if not set.
  # Config uses this to resolve the config directory.
  def self.rc_boukensha_dir
    dir = parse_rc[:boukensha_dir]
    dir ? File.expand_path(dir) : nil
  end

  def self.resolve
    # 1. BOUKENSHA_PATH env var wins.
    if ENV["BOUKENSHA_PATH"]
      dir  = File.expand_path(ENV["BOUKENSHA_PATH"])
      main = File.join(dir, "lib", "boukensha.rb")
      return main if File.exist?(main)

      abort <<~MSG
        boukensha: BOUKENSHA_PATH is set but no lib/boukensha.rb found at:
               #{dir}
               Make sure BOUKENSHA_PATH points to a step folder, e.g.:
               BOUKENSHA_PATH=~/Sites/boukensha/07_the_repl_loop boukensha
      MSG
    end

    # 2. ~/.boukensharc (BOUKENSHA_PATH key or bare path)
    rc_values = parse_rc
    if rc_values[:boukensha_path]
      raw = rc_values[:boukensha_path]
      dir  = File.expand_path(raw)
      main = File.join(dir, "lib", "boukensha.rb")
      return main if File.exist?(main)

      abort <<~MSG
        boukensha: ~/.boukensharc points to #{raw}
               but no lib/boukensha.rb was found there.
               Update ~/.boukensharc or remove it to use the bundled default.
      MSG
    end

    # 3. Bundled default.
    BUNDLED_LIB
  end

  def self.load_and_start_repl
    main = resolve
    step_dir = File.dirname(File.dirname(main))

    puts "[boukensha] loading from: #{step_dir}" if ENV["BOUKENSHA_DEBUG"]

    require main

    unless Boukensha.respond_to?(:repl)
      abort <<~MSG
        boukensha: the step at #{step_dir}
               does not support the interactive REPL (added in step 7).
               Run its examples directly, e.g.:
                 ruby #{step_dir}/examples/*.rb
               Or point BOUKENSHA_PATH at step 7 or later.
      MSG
    end

    # --no-tui falls back to the plain terminal REPL (no charm-ruby).
    no_tui = ARGV.delete("--no-tui")

    repl_opts = { tui: !no_tui }

    if ENV["MUD_NAME"]
      # Legacy env-var override still works and takes precedence over config.
      repl_opts[:working_dir] = false
      repl_opts[:mud] = {
        host:     ENV.fetch("MUD_HOST",     "localhost"),
        port:     ENV.fetch("MUD_PORT",     "4000").to_i,
        name:     ENV.fetch("MUD_NAME"),
        password: ENV.fetch("MUD_PASSWORD") { abort "boukensha: MUD_NAME is set but MUD_PASSWORD is missing." }
      }
    end
    # If MUD_NAME is not set, Boukensha.repl will fall back to config.mud_* values
    # automatically (via mud_opts_from_config inside Boukensha.repl).

    Boukensha.repl(**repl_opts)
  end
end
