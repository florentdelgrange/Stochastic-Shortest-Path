open Gauss_pivot

(* exemple 2.9 *)

let a =
  [|
    [| 1./.2.; -1./.5.; -1./.5.|];
    [| -1./.5.; 3./.5.; -1./.5.|];
    [| -1./.5.; -1./.5.; 3./.5.|]
  |]

let b = [| 5.; 3.; 2.|]

let x = resolve a b

let () =
  Array.iter (fun s -> Printf.printf "%.15F " s) x;
  Printf.printf "\n"
